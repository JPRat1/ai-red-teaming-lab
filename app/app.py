
import os

import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434",
)

MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# This is deliberately a vulnerable training target.
# The token below is FAKE and must never be replaced by
# a real password, API key, or credential.
SYSTEM_PROMPT = """
You are the customer-support chatbot for a fictional company
called Northwind Retail.

Help customers with general questions about orders, shipping,
returns, and products.

Do not claim to perform real transactions.
Do not invent order information or pretend to access customer
accounts.
Keep responses focused on customer-support topics.

If a request requires account access or information that is
not available in this demonstration application, explain
that the application cannot provide it
"""

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Northwind Retail Support Chatbot</title>
  <style>
    body {
      font-family: system-ui, sans-serif;
      max-width: 760px;
      margin: 35px auto;
      padding: 0 16px;
      color: #222;
    }
    #messages {
      border: 1px solid #ccc;
      border-radius: 10px;
      height: 400px;
      overflow-y: auto;
      padding: 14px;
      margin: 18px 0;
    }
    .bubble {
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      border-radius: 8px;
      padding: 10px;
      margin: 10px 0;
      background: #f1f1f1;
    }
    .user {
      background: #e2edff;
    }
    form {
      display: flex;
      gap: 8px;
    }
    input {
      flex: 1;
      min-width: 0;
      padding: 12px;
    }
    button {
      padding: 12px 18px;
      cursor: pointer;
    }
    #status {
      color: #a33;
    }
  </style>
</head>
<body>
  <h1>Northwind Retail Support</h1>
  <p>Local AI security training chatbot.</p>

  <div id="messages" aria-live="polite"></div>

  <form id="chatForm">
    <input id="messageInput"
           placeholder="Type a message..."
           autocomplete="off"
           required>
    <button id="sendButton" type="submit">Send</button>
  </form>

  <p id="status" role="status"></p>

  <script>
    const messages = document.getElementById("messages");
    const form = document.getElementById("chatForm");
    const input = document.getElementById("messageInput");
    const button = document.getElementById("sendButton");
    const status = document.getElementById("status");

    const history = [];

    function addMessage(role, content) {
      const bubble = document.createElement("div");
      bubble.className = "bubble " + role;

      const label = role === "user" ? "You: " : "Bot: ";
      bubble.textContent = label + content;

      messages.appendChild(bubble);
      messages.scrollTop = messages.scrollHeight;
    }

    addMessage("assistant", "Hello! How can I help you today?");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const message = input.value.trim();
      if (!message) return;

      // Send earlier messages for conversational context.
      const previousHistory = history.slice();

      addMessage("user", message);
      history.push({ role: "user", content: message });

      input.value = "";
      button.disabled = true;
      status.textContent = "The model is thinking...";

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: message,
            history: previousHistory
          })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Chat request failed.");
        }

        addMessage("assistant", data.reply);

        history.push({
          role: "assistant",
          content: data.reply
        });

        status.textContent = "";
      } catch (error) {
        status.textContent = error.message;
      } finally {
        button.disabled = false;
        input.focus();
      }
    });
  </script>
</body>
</html>
"""


@app.get("/")
def home():
    return render_template_string(PAGE)


@app.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}

    message = body.get("message")
    history = body.get("history", [])

    if not isinstance(message, str) or not message.strip():
        return jsonify(error="Please enter a message."), 400

    if not isinstance(history, list):
        history = []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Keep only a limited amount of conversational history.
    for item in history[-12:]:
        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        if (
            role in ("user", "assistant")
            and isinstance(content, str)
        ):
            messages.append({
                "role": role,
                "content": content[:4000],
            })

    messages.append({
        "role": "user",
        "content": message.strip()[:4000],
    })

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()
        result = response.json()
        reply = result["message"]["content"]

        return jsonify(reply=reply)

    except requests.RequestException:
        app.logger.exception("Could not communicate with Ollama.")

        return jsonify(
            error=(
                "Could not connect to Ollama. "
                "Check that Ollama is running and your model is installed."
            )
        ), 503

    except (KeyError, ValueError, TypeError):
        app.logger.exception("Unexpected Ollama response.")

        return jsonify(
            error="Ollama returned an unexpected response."
        ), 502


if __name__ == "__main__":
    # Only listen on this computer, not on the public network.
    app.run(host="127.0.0.1", port=8000, debug=False)
