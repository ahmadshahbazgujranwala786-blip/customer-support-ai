(() => {
  "use strict";

  const STORAGE = {
    api: "agenticflow.support.apiEndpoint",
    theme: "agenticflow.support.theme",
    visitor: "agenticflow.support.visitorId",
    history: "agenticflow.support.conversations"
  };

  const $ = (selector) => document.querySelector(selector);
  const els = {
    body: document.body,
    sidebar: $("#sidebar"),
    mobileScrim: $("#mobileScrim"),
    openSidebar: $("#openSidebar"),
    closeSidebar: $("#closeSidebar"),
    newChatButton: $("#newChatButton"),
    conversationList: $("#conversationList"),
    clearHistoryButton: $("#clearHistoryButton"),
    connectionPill: $("#connectionPill"),
    connectionDot: $("#connectionDot"),
    connectionLabel: $("#connectionLabel"),
    themeButton: $("#themeButton"),
    helpButton: $("#helpButton"),
    settingsButton: $("#settingsButton"),
    apiConfigInline: $("#apiConfigInline"),
    chatCanvas: $("#chatCanvas"),
    welcomeState: $("#welcomeState"),
    suggestionGrid: $("#suggestionGrid"),
    messageList: $("#messageList"),
    scrollAnchor: $("#scrollAnchor"),
    messageInput: $("#messageInput"),
    sendButton: $("#sendButton"),
    charCount: $("#charCount"),
    settingsDialog: $("#settingsDialog"),
    settingsForm: $("#settingsForm"),
    apiEndpoint: $("#apiEndpoint"),
    connectionDetail: $("#connectionDetail"),
    testConnectionButton: $("#testConnectionButton"),
    saveEndpointButton: $("#saveEndpointButton"),
    closeSettings: $("#closeSettings"),
    helpDialog: $("#helpDialog"),
    toastRegion: $("#toastRegion")
  };

  const savedApiEndpoint = localStorage.getItem(STORAGE.api);
  // On the public site the UI is served by the API itself, so use same-origin
  // requests. The separate local dev server on port 5173 targets the local API.
  const defaultApiEndpoint = window.location.port === "5173"
    ? "http://127.0.0.1:8000/api/chat"
    : "/api/chat";
  // Migrate stale same-origin/static-server URLs: Python's simple HTTP server
  // serves the frontend but cannot accept POST chat requests (HTTP 501).
  const initialApiEndpoint = (() => {
    if (!savedApiEndpoint || savedApiEndpoint === "/api/chat") return defaultApiEndpoint;
    try {
      const savedUrl = new URL(savedApiEndpoint, window.location.href);
      if (savedUrl.pathname.endsWith("/api/chat") &&
          (savedUrl.port === "5173" ||
           ((savedUrl.hostname === "127.0.0.1" || savedUrl.hostname === "localhost") && window.location.port !== "5173") ||
           savedUrl.origin === window.location.origin && !savedUrl.port)) {
        return defaultApiEndpoint;
      }
    } catch {
      return defaultApiEndpoint;
    }
    return savedApiEndpoint;
  })();
  if (initialApiEndpoint !== savedApiEndpoint) {
    localStorage.setItem(STORAGE.api, initialApiEndpoint);
  }

  const state = {
    apiEndpoint: initialApiEndpoint,
    theme: localStorage.getItem(STORAGE.theme) || "dark",
    visitorId: getVisitorId(),
    conversations: loadConversations(),
    activeConversationId: null,
    sending: false
  };

  function makeId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    return "visit-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }

  function getVisitorId() {
    let value = localStorage.getItem(STORAGE.visitor);
    if (!value) {
      value = makeId();
      localStorage.setItem(STORAGE.visitor, value);
    }
    return value;
  }

  function loadConversations() {
    try {
      const data = JSON.parse(localStorage.getItem(STORAGE.history) || "[]");
      return Array.isArray(data)
        ? data.filter((item) => item && typeof item.id === "string" && Array.isArray(item.messages))
        : [];
    } catch {
      return [];
    }
  }

  function persistConversations() {
    try {
      localStorage.setItem(STORAGE.history, JSON.stringify(state.conversations.slice(0, 30)));
    } catch {
      toast("Conversation history could not be saved in this browser.", "warning");
    }
  }

  function currentConversation() {
    return state.conversations.find((item) => item.id === state.activeConversationId) || null;
  }

  function createConversation() {
    const conversation = {
      id: makeId(),
      title: "New conversation",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: []
    };
    state.conversations.unshift(conversation);
    state.activeConversationId = conversation.id;
    renderConversationList();
    renderMessages();
    closeSidebar();
    els.messageInput.focus();
  }

  function activateConversation(id) {
    if (!state.conversations.some((item) => item.id === id)) return;
    state.activeConversationId = id;
    renderConversationList();
    renderMessages();
    closeSidebar();
  }

  function ensureActiveConversation() {
    let conversation = currentConversation();
    if (!conversation) {
      conversation = {
        id: makeId(),
        title: "New conversation",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messages: []
      };
      state.conversations.unshift(conversation);
      state.activeConversationId = conversation.id;
    }
    return conversation;
  }

  function formatTime(value) {
    try {
      return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(new Date(value));
    } catch {
      return "";
    }
  }

  function formatRelativeDate(value) {
    const date = new Date(value);
    const today = new Date();
    const sameDay = date.toDateString() === today.toDateString();
    if (sameDay) return "Today";
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
    return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(date);
  }

  function createSvgIcon(name) {
    const paths = {
      chat: '<path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H7l-3.5 2V7.5A7.5 7.5 0 0 1 11 0h1.5A7.5 7.5 0 0 1 20 7.5v4Z" transform="translate(2 1) scale(.88)"/>',
      copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
      check: '<path d="m5 12 4 4L19 6"/>',
      alert: '<path d="M12 3 2.8 19h18.4L12 3Z"/><path d="M12 9v4m0 3h.01"/>'
    };
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    svg.innerHTML = paths[name] || paths.chat;
    return svg;
  }

  function renderConversationList() {
    els.conversationList.replaceChildren();
    const sorted = [...state.conversations]
      .filter((conversation) => conversation.messages.length > 0)
      .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
      .slice(0, 16);

    if (!sorted.length) {
      const empty = document.createElement("div");
      empty.className = "empty-history";
      const icon = document.createElement("span");
      icon.className = "history-icon";
      icon.textContent = "◷";
      const text = document.createElement("span");
      text.textContent = "Your conversations will appear here.";
      empty.append(icon, text);
      els.conversationList.append(empty);
      return;
    }

    sorted.forEach((conversation) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "conversation-entry" + (conversation.id === state.activeConversationId ? " selected" : "");
      button.setAttribute("aria-label", "Open conversation: " + conversation.title);
      const icon = document.createElement("span");
      icon.className = "entry-icon";
      icon.append(createSvgIcon("chat"));
      const copy = document.createElement("span");
      copy.className = "entry-copy";
      const title = document.createElement("strong");
      title.textContent = conversation.title || "Conversation";
      const meta = document.createElement("small");
      meta.textContent = formatRelativeDate(conversation.updatedAt || conversation.createdAt);
      copy.append(title, meta);
      button.append(icon, copy);
      button.addEventListener("click", () => activateConversation(conversation.id));
      els.conversationList.append(button);
    });
  }

  function addMessageElement(message, index) {
    const row = document.createElement("article");
    row.className = "chat-message " + (message.role === "user" ? "user" : "assistant");
    row.dataset.messageIndex = String(index);

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    if (message.role === "user") {
      avatar.textContent = "You";
    } else {
      avatar.innerHTML = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 4.5 24.5 15.5 35.5 20 24.5 24.5 20 35.5 15.5 24.5 4.5 20 15.5 15.5 20 4.5Z" fill="currentColor" stroke="none"/><circle cx="20" cy="20" r="4" fill="#101827" stroke="none"/></svg>';
    }

    const body = document.createElement("div");
    body.className = "message-body";
    const meta = document.createElement("div");
    meta.className = "message-meta";
    const author = document.createElement("strong");
    author.textContent = message.role === "user" ? "You" : "Support Assistant";
    const time = document.createElement("time");
    time.dateTime = message.timestamp || new Date().toISOString();
    time.textContent = formatTime(message.timestamp || Date.now());
    meta.append(author, time);

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message.content || "";
    body.append(meta, content);

    if (message.role !== "user" && message.content && !message.pending && !message.error) {
      const tools = document.createElement("div");
      tools.className = "message-tools";
      const copyButton = document.createElement("button");
      copyButton.type = "button";
      copyButton.append(createSvgIcon("copy"), document.createTextNode("Copy"));
      copyButton.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(message.content);
          copyButton.replaceChildren(createSvgIcon("check"), document.createTextNode("Copied"));
          window.setTimeout(() => {
            if (copyButton.isConnected) copyButton.replaceChildren(createSvgIcon("copy"), document.createTextNode("Copy"));
          }, 1400);
        } catch {
          toast("Copy isn't available in this browser context.", "warning");
        }
      });
      tools.append(copyButton);
      body.append(tools);
    }

    row.append(avatar, body);
    els.messageList.append(row);
  }

  function renderTypingIndicator() {
    const row = document.createElement("article");
    row.className = "chat-message assistant typing-message";
    row.id = "typingIndicator";
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.innerHTML = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 4.5 24.5 15.5 35.5 20 24.5 24.5 20 35.5 15.5 24.5 4.5 20 15.5 15.5 20 4.5Z" fill="currentColor" stroke="none"/><circle cx="20" cy="20" r="4" fill="#101827" stroke="none"/></svg>';
    const body = document.createElement("div");
    body.className = "message-body";
    const meta = document.createElement("div");
    meta.className = "message-meta";
    const author = document.createElement("strong");
    author.textContent = "Support Assistant";
    meta.append(author);
    const dots = document.createElement("div");
    dots.className = "typing-dots";
    dots.setAttribute("aria-label", "Assistant is responding");
    dots.innerHTML = "<i></i><i></i><i></i>";
    body.append(meta, dots);
    row.append(avatar, body);
    els.messageList.append(row);
    scrollToBottom();
  }

  function renderMessages() {
    const conversation = currentConversation();
    const messages = conversation ? conversation.messages : [];
    const hasMessages = messages.length > 0;
    els.welcomeState.hidden = hasMessages;
    els.messageList.hidden = !hasMessages;
    els.messageList.replaceChildren();

    if (hasMessages) {
      messages.forEach((message, index) => addMessageElement(message, index));
    }
    updateComposer();
    scrollToBottom();
  }

  function scrollToBottom() {
    window.requestAnimationFrame(() => {
      els.chatCanvas.scrollTop = els.chatCanvas.scrollHeight;
    });
  }

  function updateComposer() {
    const value = els.messageInput.value;
    els.charCount.textContent = value.length + " / 4000";
    els.sendButton.disabled = state.sending || !value.trim();
    els.sendButton.title = state.sending ? "Sending…" : "Send message";
  }

  function pushMessage(role, content, extra = {}) {
    const conversation = ensureActiveConversation();
    const message = {
      role,
      content: String(content ?? ""),
      timestamp: new Date().toISOString(),
      ...extra
    };
    conversation.messages.push(message);
    conversation.updatedAt = message.timestamp;
    if (role === "user" && conversation.title === "New conversation") {
      const firstLine = message.content.trim().split(/\r?\n/)[0];
      conversation.title = firstLine.length > 35 ? firstLine.slice(0, 35).trimEnd() + "…" : firstLine;
    }
    persistConversations();
    renderConversationList();
    renderMessages();
    return message;
  }

  function normalizeApiResponse(data) {
    if (typeof data === "string") return data.trim();
    if (!data || typeof data !== "object") return "";
    const candidates = [
      data.reply, data.response, data.final_response, data.answer, data.output,
      data.message, data.data && data.data.reply, data.data && data.data.response,
      data.data && data.data.final_response, data.result && data.result.reply
    ];
    for (const candidate of candidates) {
      if (typeof candidate === "string" && candidate.trim()) return candidate.trim();
    }
    if (data.error && typeof data.error === "string") throw new Error(data.error);
    return "";
  }

  function healthUrlFromChatEndpoint(endpoint) {
    const clean = endpoint.replace(/\/+$/, "");
    if (clean.endsWith("/api/chat")) return clean.slice(0, -"/api/chat".length) + "/health";
    if (clean.endsWith("/chat")) return clean.slice(0, -"/chat".length) + "/health";
    return clean + "/health";
  }

  function absoluteApiEndpoint(endpoint) {
    return new URL(endpoint, window.location.href).href;
  }

  function setConnectionStatus(status, label, detail) {
    els.connectionPill.classList.remove("connected", "error");
    els.connectionDetail.classList.remove("connected", "error");
    if (status === "connected") {
      els.connectionPill.classList.add("connected");
      els.connectionLabel.textContent = "Backend connected";
      els.connectionDetail.classList.add("connected");
      els.connectionDetail.querySelector("span:last-child").textContent = detail || "Backend is responding.";
    } else if (status === "error") {
      els.connectionPill.classList.add("error");
      els.connectionLabel.textContent = "Backend offline";
      els.connectionDetail.classList.add("error");
      els.connectionDetail.querySelector("span:last-child").textContent = detail || "The endpoint could not be reached.";
    } else {
      els.connectionLabel.textContent = label || "Checking backend";
      els.connectionDetail.querySelector("span:last-child").textContent = detail || "Checking the configured endpoint…";
    }
  }

  async function checkConnection(showToast = false, endpointOverride = state.apiEndpoint) {
    const endpointValue = String(endpointOverride || "").trim();
    if (!endpointValue) {
      setConnectionStatus("error", "", "Set a chat API endpoint to connect the website.");
      return false;
    }
    setConnectionStatus("checking", "Checking backend", "Trying to reach the backend health endpoint…");
    try {
      const endpoint = absoluteApiEndpoint(healthUrlFromChatEndpoint(endpointValue));
      const response = await fetch(endpoint, { method: "GET", headers: { Accept: "application/json" }, signal: AbortSignal.timeout(5000) });
      if (!response.ok) throw new Error("Health endpoint returned HTTP " + response.status + ".");
      const payload = await response.json().catch(() => ({}));
      if (payload.status && !["ok", "healthy", "ready"].includes(String(payload.status).toLowerCase())) {
        throw new Error("Health endpoint reported status: " + payload.status);
      }
      setConnectionStatus("connected", "", "Backend responded at " + endpoint);
      if (showToast) toast("Backend connection looks good.", "success");
      return true;
    } catch (error) {
      const message = error && error.name === "TimeoutError"
        ? "The health check timed out. Check the server address and whether the backend is running."
        : "Could not reach the health endpoint. Start the API and check CORS settings.";
      setConnectionStatus("error", "", message);
      if (showToast) toast(message, "warning");
      return false;
    }
  }

  async function sendMessage(text = els.messageInput.value) {
    const message = String(text || "").trim();
    if (!message || state.sending) return;
    if (message.length > 4000) {
      toast("Please keep your message under 4,000 characters.", "warning");
      return;
    }

    if (!currentConversation() || (currentConversation() && currentConversation().messages.length > 0 && !state.activeConversationId)) {
      ensureActiveConversation();
    }

    pushMessage("user", message);
    els.messageInput.value = "";
    autoResizeInput();
    state.sending = true;
    updateComposer();
    renderTypingIndicator();

    try {
      const endpoint = absoluteApiEndpoint(state.apiEndpoint.trim() || "/api/chat");
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          message,
          user_id: state.visitorId,
          channel: "web",
          sender_name: "Website Visitor"
        }),
        signal: AbortSignal.timeout(90000)
      });

      const payload = await response.text();
      let data = payload;
      try { data = payload ? JSON.parse(payload) : {}; } catch { /* plain-text response is supported */ }
      if (!response.ok) {
        const detail = data && typeof data === "object" ? (data.detail || data.error || data.message) : data;
        const isHtml = typeof detail === "string" && /<(?:!doctype|html|body|pre)\b/i.test(detail);
        if (isHtml) {
          throw new Error(
            "The configured server returned HTML instead of a chat API response (HTTP " + response.status +
            "). Start the Python API and use http://127.0.0.1:8000/api/chat."
          );
        }
        throw new Error(detail ? String(detail) : "The server returned HTTP " + response.status + ".");
      }
      const reply = normalizeApiResponse(data);
      if (!reply) throw new Error("The API responded, but no reply field was found. Return a JSON field named reply or final_response.");
      const indicator = $("#typingIndicator");
      if (indicator) indicator.remove();
      pushMessage("assistant", reply);
      setConnectionStatus("connected", "");
    } catch (error) {
      const indicator = $("#typingIndicator");
      if (indicator) indicator.remove();
      const detail = error && error.name === "TimeoutError"
        ? "The response took too long. The backend may still be processing your request."
        : error && error.message
          ? error.message
          : "The backend could not be reached.";
      pushMessage("assistant", "I couldn't get a response from the support service. " + detail + "\n\nCheck the backend connection settings and try again.");
      setConnectionStatus("error", "", "The chat request failed. Check the API endpoint, server logs and CORS configuration.");
    } finally {
      state.sending = false;
      updateComposer();
      els.messageInput.focus();
    }
  }

  function autoResizeInput() {
    els.messageInput.style.height = "auto";
    els.messageInput.style.height = Math.min(els.messageInput.scrollHeight, 155) + "px";
    updateComposer();
  }

  function toast(message, type = "info") {
    const item = document.createElement("div");
    item.className = "toast";
    const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    icon.setAttribute("viewBox", "0 0 24 24");
    icon.innerHTML = type === "success"
      ? '<path d="m5 12 4 4L19 6"/>'
      : '<path d="M12 3 2.8 19h18.4L12 3Z"/><path d="M12 9v4m0 3h.01"/>';
    const text = document.createElement("span");
    text.textContent = message;
    item.append(icon, text);
    els.toastRegion.append(item);
    window.setTimeout(() => item.remove(), 4500);
  }

  function showSettings() {
    els.apiEndpoint.value = state.apiEndpoint;
    setConnectionStatus("checking", "", "Check that the URL points to a reachable backend.");
    els.settingsDialog.showModal();
    window.setTimeout(() => els.apiEndpoint.focus(), 60);
  }

  function closeSidebar() {
    els.body.classList.remove("sidebar-open");
  }

  function toggleSidebar() {
    els.body.classList.toggle("sidebar-open");
  }

  function applyTheme(theme) {
    state.theme = theme === "light" ? "light" : "dark";
    els.body.classList.toggle("light-theme", state.theme === "light");
    localStorage.setItem(STORAGE.theme, state.theme);
    els.themeButton.innerHTML = state.theme === "light"
      ? '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></svg>'
      : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 15.5A8.5 8.5 0 0 1 8.5 3.5a8.5 8.5 0 1 0 12 12Z"/></svg>';
  }

  els.newChatButton.addEventListener("click", createConversation);
  els.openSidebar.addEventListener("click", toggleSidebar);
  els.closeSidebar.addEventListener("click", closeSidebar);
  els.mobileScrim.addEventListener("click", closeSidebar);
  els.connectionPill.addEventListener("click", showSettings);
  els.settingsButton.addEventListener("click", showSettings);
  els.apiConfigInline.addEventListener("click", showSettings);
  els.closeSettings.addEventListener("click", () => els.settingsDialog.close());
  els.helpButton.addEventListener("click", () => els.helpDialog.showModal());
  els.themeButton.addEventListener("click", () => applyTheme(state.theme === "dark" ? "light" : "dark"));
  els.testConnectionButton.addEventListener("click", async () => {
    const candidate = els.apiEndpoint.value.trim();
    if (!candidate) {
      setConnectionStatus("error", "", "Enter an API endpoint first.");
      return;
    }
    els.testConnectionButton.disabled = true;
    els.testConnectionButton.textContent = "Testing…";
    await checkConnection(true, candidate);
    els.testConnectionButton.disabled = false;
    els.testConnectionButton.textContent = "Test connection";
  });
  els.saveEndpointButton.addEventListener("click", () => {
    const candidate = els.apiEndpoint.value.trim();
    if (!candidate) {
      toast("Enter a chat API endpoint before saving.", "warning");
      els.apiEndpoint.focus();
      return;
    }
    try {
      new URL(candidate, window.location.href);
    } catch {
      toast("Enter a valid URL, such as http://127.0.0.1:8000/api/chat.", "warning");
      return;
    }
    state.apiEndpoint = candidate;
    localStorage.setItem(STORAGE.api, candidate);
    els.settingsDialog.close();
    toast("Backend endpoint saved in this browser.", "success");
    checkConnection();
  });
  els.settingsDialog.addEventListener("click", (event) => {
    if (event.target === els.settingsDialog) els.settingsDialog.close();
  });
  els.helpDialog.addEventListener("click", (event) => {
    if (event.target === els.helpDialog) els.helpDialog.close();
  });

  els.messageInput.addEventListener("input", autoResizeInput);
  els.messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      sendMessage();
    }
  });
  els.sendButton.addEventListener("click", () => sendMessage());

  els.suggestionGrid.addEventListener("click", (event) => {
    const card = event.target.closest("[data-prompt]");
    if (!card || state.sending) return;
    els.messageInput.value = card.dataset.prompt || "";
    autoResizeInput();
    els.messageInput.focus();
  });

  els.clearHistoryButton.addEventListener("click", () => {
    if (!state.conversations.some((item) => item.messages.length)) {
      toast("There is no saved conversation history to clear.");
      return;
    }
    if (!window.confirm("Clear conversation history saved in this browser? This cannot be undone.")) return;
    state.conversations = [];
    state.activeConversationId = null;
    persistConversations();
    renderConversationList();
    renderMessages();
    toast("Local conversation history cleared.", "success");
  });

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      createConversation();
    }
    if (event.key === "Escape") closeSidebar();
  });

  document.querySelectorAll("[data-nav]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.nav !== "inbox") {
        toast("The knowledge-management view isn't connected in this frontend yet.");
        return;
      }
      document.querySelectorAll("[data-nav]").forEach((item) => item.classList.toggle("active", item === button));
      closeSidebar();
    });
  });

  applyTheme(state.theme);
  renderConversationList();
  const latestSaved = [...state.conversations]
    .filter((conversation) => conversation.messages.length > 0)
    .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))[0];
  if (latestSaved) {
    state.activeConversationId = latestSaved.id;
    renderConversationList();
  }
  renderMessages();
  checkConnection();
})();