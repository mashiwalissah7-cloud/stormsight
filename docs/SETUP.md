# Finish connecting StormSight

The local app works without API keys. The hackathon entry still needs a successful NVIDIA model call through Nebius, a public repository, a hosted demo, and a public YouTube video.

## Nebius connection

1. Open Token Factory and sign in to your account.
2. Confirm that the account has usable credits or billing that you choose to enable. Builder Program approval and Token Factory account access are separate steps.
3. In the model catalog, find an NVIDIA Nemotron model. Copy the exact model identifier and HTTPS base URL from its dashboard example. Do not guess either value.
4. Create an API key in your own account. Do not paste it into chat or commit it to GitHub.
5. Copy `.env.example` to `.env` locally. Fill the three Nebius fields using the dashboard values.
6. Restart the local Streamlit process and click Generate Nemotron briefing. Verify the tool trace, model ID, and returned text. A configuration badge alone does not prove connectivity.

Native function calling support has not been verified. The implementation uses a JSON plan, validates tool names, runs Python tools, and then asks for qualitative prose. Numerical tables are rendered by Python. Invalid generated prose is rejected and retried once.

## Tavily

Create a Tavily account and key if you want the optional official source lookup. Put the key in `TAVILY_API_KEY` in `.env`. The lookup sends only the selected storm name and year. It is optional for the local data explorer but must be tested before claiming a working Tavily integration in the submission.

## GitHub Desktop

Review the Changes tab before committing. Expected files are source code, public source data, county aggregates, model artifacts, tests, documentation, and configuration templates. Never include `.env`, `.streamlit/secrets.toml`, `.venv`, `work`, or raw claim caches.

Use a descriptive commit summary. Publish the repository publicly only when the review is clean. The MIT license is already included.

## Streamlit Community Cloud

Use the official deployment page at https://share.streamlit.io/. Sign in with the account that can access your public repository. Select the repository, main branch, and `app.py` entrypoint. Select Python 3.14 if available, since that is the tested local runtime. If it is unavailable, test a supported runtime before deployment rather than assuming compatibility.

In Advanced settings, add secrets using TOML syntax:

```toml
NEBIUS_API_KEY = "your private key"
NEBIUS_BASE_URL = "exact dashboard URL"
NEBIUS_MODEL = "exact dashboard NVIDIA model ID"
TAVILY_API_KEY = "your private key"
```

Do not place real secrets in a repository file. Verify the public app in a signed out browser. A localhost address cannot be used by judges on another computer.

Official deployment instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Final submission

Use the actual public repository and app URLs. Record a public YouTube video under three minutes showing real behavior, validation, and limitations. Do not claim an NVIDIA or Tavily call succeeded until it actually has. Review the complete official rules before final submission.
