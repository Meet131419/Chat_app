self.addEventListener("push", (event) => {
    console.log("🔥 Push Event Received ✅:", event);

    let data = event.data ? event.data.json() : {};
    console.log("📩 Push Data Received:", data);

    const title = data.title || "New Chat Message";
    const options = {
        body: data.body || "You have a new message",
        icon: "/static/images/icon.png",
        badge: "/static/images/badge.png",
        vibrate: [200, 100, 200], 
        tag: "chat-message",
        requireInteraction: true,
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("message", (event) => {
    console.log("📩 Message received in Service Worker:", event.data);
    if (event.data && event.data.type === "push") {
        const { title, body } = event.data;
        self.registration.showNotification(title, { body });
    }
});

self.addEventListener("sync", (event) => {
    console.log("⏳ Background Sync Triggered ✅", event);
});
  