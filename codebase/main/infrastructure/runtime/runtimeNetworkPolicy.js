const LOOPBACK_HOSTS = new Set(["localhost", "127.0.0.1", "::1"]);
const LOCAL_SCHEMES = new Set(["data:", "blob:"]);
const NETWORK_SCHEMES = new Set(["http:", "https:", "ws:", "wss:"]);

function normalizeHostname(hostname) {
  const normalized = String(hostname || "").toLowerCase();
  return normalized.startsWith("[") && normalized.endsWith("]")
    ? normalized.slice(1, -1)
    : normalized;
}

function hasExactLoopbackAuthority(value) {
  const match = value.match(/^[a-z][a-z\d+.-]*:\/\/([^/?#]*)/i);
  if (!match) return false;
  return /^(?:localhost|127\.0\.0\.1|\[::1\])(?::\d{1,5})?$/i.test(match[1]);
}

function isAllowedRuntimeUrl(value) {
  if (typeof value !== "string" || value.length === 0) return false;

  let url;
  try {
    url = new URL(value);
  } catch {
    return false;
  }

  if (url.protocol === "file:") {
    const hostname = normalizeHostname(url.hostname);
    return hostname === "" || hostname === "localhost";
  }
  if (LOCAL_SCHEMES.has(url.protocol)) return true;
  if (url.protocol === "about:") return url.href === "about:blank";
  if (!NETWORK_SCHEMES.has(url.protocol)) return false;

  return (
    LOOPBACK_HOSTS.has(normalizeHostname(url.hostname)) && hasExactLoopbackAuthority(value)
  );
}

function installRuntimeNetworkPolicy(electronSession, logger = console, electronApp = null) {
  if (!electronSession?.webRequest) {
    throw new TypeError("An Electron session with webRequest is required");
  }

  electronSession.webRequest.onBeforeRequest((details, callback) => {
    const allowed = isAllowedRuntimeUrl(details.url);
    if (!allowed) {
      logger.warn?.("Blocked external runtime request", {
        url: details.url,
        resourceType: details.resourceType,
      });
    }
    callback({ cancel: !allowed });
  });

  electronSession.webRequest.onBeforeRedirect((details) => {
    if (!isAllowedRuntimeUrl(details.redirectURL)) {
      logger.warn?.("Blocked external runtime redirect", {
        from: details.url,
        to: details.redirectURL,
      });
    }
  });

  electronApp?.on?.("web-contents-created", (_event, contents) => {
    const blockExternalNavigation = (event, url) => {
      if (isAllowedRuntimeUrl(url)) return;
      event.preventDefault();
      logger.warn?.("Blocked external navigation", { url });
    };

    contents.on("will-navigate", blockExternalNavigation);
    contents.on("will-redirect", blockExternalNavigation);
    contents.on("will-attach-webview", (event) => event.preventDefault());
    contents.setWindowOpenHandler(({ url }) => {
      logger.warn?.("Blocked new window", { url });
      return { action: "deny" };
    });
  });
}

module.exports = { isAllowedRuntimeUrl, installRuntimeNetworkPolicy };
