import e2b
from interpreter import interpreter
import os
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

load_dotenv()

import os
os.environ["E2B_API_KEY"] = "e2b_73dc685aa5877f574f7756f8cab53d1f465f6fee"

class PythonE2B:
    def __init__(self):
        super().__init__()

    """
    This class contains all requirements for being a custom language in Open Interpreter:

    - name (an attribute)
    - run (a method)
    - stop (a method)
    - terminate (a method)

    Here, we'll use E2B to power the `run` method.
    """

    # This is the name that will appear to the LLM.
    name = "python"

    # Optionally, you can append some information about this language to the system message:
    system_message = "# Follow this rule: Every Python code block MUST contain at least one print statement."

    # (E2B isn't a Jupyter Notebook, so we added ^ this so it would print things,
    # instead of putting variables at the end of code blocks, which is a Jupyter thing.)

    def run(self, code):
        """Generator that yields a dictionary in LMC Format."""
        # Load a Sandbox
        sbx = Sandbox()
        
        # Run the code on E2B
        output = sbx.run_code(code)
        print(output)

        # Yield the output
        return {
            "type": "console", "format": "output",
            "content": output.logs.stdout # We combined these arbitrarily. Yield anything you'd like!
        }

    def stop(self):
        """Stops the code."""
        # Not needed here, because e2b.run_code isn't stateful.
        pass

    def terminate(self):
        """Terminates the entire process."""
        # Not needed here, because e2b.run_code isn't stateful.
        pass

# (Tip: Do this before adding/removing languages, otherwise OI might retain the state of previous languages:)

# Give Open Interpreter its languages. This will only let it run PythonE2B:
interpreter.computer.languages = [PythonE2B]
interpreter.llm.interpreter.safe_mode = False
# Try it out!
interpreter.chat("What's 349808*38490739 run code?", stream=False, display=True)
