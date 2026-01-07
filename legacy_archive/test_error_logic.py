from LLM_Provider import LLMProvider

llm = LLMProvider(model_name="gemini-1.5-flash")

print("--- Testing Error Resolution ---")
cmd = "cat /etc/shadow"
error = "cat: /etc/shadow: Permission denied"
user = "dev_alice"

print(f"Scenario: {user} tried '{cmd}' and got '{error}'")
resolution = llm.resolve_error(cmd, error, user)

print("\nLLM Decision:")
print(f"Action: {resolution.get('action')}")
print(f"Target User: {resolution.get('target_user')}")
print(f"Fix Command: {resolution.get('fix_command')}")
print(f"Reason: {resolution.get('reason')}")
