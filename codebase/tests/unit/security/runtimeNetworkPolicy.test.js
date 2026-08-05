const test = require("node:test");
const assert = require("node:assert/strict");
const {
  isAllowedRuntimeUrl,
  installRuntimeNetworkPolicy,
} = require("../../../main/infrastructure/runtime/runtimeNetworkPolicy");

test("runtime URL policy permits only local schemes and exact loopback hosts", () => {
  for (const url of [
    "file:///tmp/index.html",
    "file://localhost/tmp/index.html",
    "data:text/plain,hello",
    "blob:file:///local-id",
    "about:blank",
    "http://localhost:3000/",
    "https://127.0.0.1:8178/",
    "ws://[::1]:6333/",
  ]) {
    assert.equal(isAllowedRuntimeUrl(url), true, url);
  }

  for (const url of [
    "https://example.com/",
    "wss://api.example.com/",
    "https://localhost.example.com/",
    "https://127.0.0.1.example.com/",
    "https://localhost@evil.example/",
    "https://2130706433/",
    "file://server/share/index.html",
    "file://127.0.0.1/share/index.html",
    "app://renderer/index.html",
    "mnemora://local/path",
    "ftp://127.0.0.1/file",
    "javascript:alert(1)",
    "not a url",
  ]) {
    assert.equal(isAllowedRuntimeUrl(url), false, url);
  }
});

test("session policy cancels external requests and observes external redirects", () => {
  const listeners = {};
  const warnings = [];
  const fakeSession = {
    webRequest: {
      onBeforeRequest(listener) {
        listeners.request = listener;
      },
      onBeforeRedirect(listener) {
        listeners.redirect = listener;
      },
    },
  };
  const appListeners = {};
  const fakeApp = {
    on(event, listener) {
      appListeners[event] = listener;
    },
  };

  installRuntimeNetworkPolicy(
    fakeSession,
    { warn: (...args) => warnings.push(args) },
    fakeApp
  );

  let decision;
  listeners.request({ url: "http://127.0.0.1:8178/", resourceType: "xhr" }, (value) => {
    decision = value;
  });
  assert.deepEqual(decision, { cancel: false });

  listeners.request({ url: "https://example.com/", resourceType: "xhr" }, (value) => {
    decision = value;
  });
  assert.deepEqual(decision, { cancel: true });

  listeners.redirect({ url: "http://localhost:3000/", redirectURL: "https://example.com/" });

  const contentListeners = {};
  let openHandler;
  appListeners["web-contents-created"]({}, {
    on(event, listener) {
      contentListeners[event] = listener;
    },
    setWindowOpenHandler(listener) {
      openHandler = listener;
    },
  });
  let prevented = false;
  contentListeners["will-redirect"](
    { preventDefault: () => (prevented = true) },
    "https://example.com/"
  );
  assert.equal(prevented, true);
  assert.deepEqual(openHandler({ url: "https://example.com/" }), { action: "deny" });
  assert.equal(warnings.length, 4);
});
