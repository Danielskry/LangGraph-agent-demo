
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import importlib.util
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

# Try to import main.py once at module load to avoid re-initializing models on every request.
main = None
def _import_main_module(path: Path):
	"""Import the user's top-level main.py under a non-conflicting module name and validate it.

	Returns the module object or raises an exception.
	"""
	module_name = "chat_main"
	spec = importlib.util.spec_from_file_location(module_name, str(path))
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	# Validate expected entry point
	if not hasattr(mod, "chatbot_response"):
		raise ImportError(f"Imported module {module_name} missing 'chatbot_response'; attrs: {dir(mod)}")
	return mod

try:
	main_path = Path(__file__).resolve().parent.parent.parent / "main.py"
	main = _import_main_module(main_path)
	logger.info("Imported main.py successfully at startup")
except Exception as e:
	# If import fails here, we'll attempt to import lazily per-request and return errors gracefully.
	logger.exception("Initial import of main.py failed: %s", e)


def index(request):
	return render(request, 'index.html')


# Run the chatbot call in a thread with a timeout to avoid blocking the dev server
@csrf_exempt
def run_script(request):
	if request.method != "POST":
		return JsonResponse({"error": "POST request required."}, status=400)

	user_input = request.POST.get("message", "")
	# Ensure main module is loaded; try lazy import if startup import failed
	global main
	if main is None:
		try:
			main_path = Path(__file__).resolve().parent.parent.parent / "main.py"
			main = _import_main_module(main_path)
			logger.info("Imported main.py on-demand")
		except Exception as e:
			logger.exception("Failed to import main.py on-demand: %s", e)
			return JsonResponse({"error": f"Server import error: {e}"}, status=500)

	# Use a ThreadPoolExecutor to allow a timeout
	# Allow a bit more time for the model to respond locally
	timeout_seconds = 60
	with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
		future = executor.submit(main.chatbot_response, user_input)
		try:
			response = future.result(timeout=timeout_seconds)
			# Log the exact response we will send to the client for debugging
			try:
				resp_snippet = response if isinstance(response, str) else repr(response)
			except Exception:
				resp_snippet = '<unrepresentable response>'
			logger.info('chatbot_response returned (type=%s): %s', type(response).__name__, (resp_snippet[:1000] + '...') if len(str(resp_snippet)) > 1000 else resp_snippet)
			# Ensure we return a plain text string to the client (extract .content if AIMessage-like)
			try:
				output_text = response.content if hasattr(response, 'content') else str(response)
			except Exception:
				output_text = str(response)
			# Also print to stdout so it's visible in dev server console
			print(f"[run_script] Returning output (len={len(output_text)}): {output_text[:1000]}{'...' if len(output_text) > 1000 else ''}")
			return JsonResponse({"output": output_text})
		except concurrent.futures.TimeoutError:
			logger.warning("chatbot_response timed out after %s seconds", timeout_seconds)
			# Attempt to cancel and return timeout to client quickly
			future.cancel()
			return JsonResponse({"error": "Processing timeout. Try again or simplify the query."}, status=504)
		except Exception as e:
			logger.exception("Error while running chatbot_response")
			return JsonResponse({"error": f"Server error: {e}"}, status=500)
