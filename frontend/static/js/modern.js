// ====================== modern.js - نسخة فاخرة 2025 ======================
const messagesArea = document.getElementById("messages-area");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");

let _isLoading = false; // منع إرسال رسايل متعددة

const welcomeHTML = `
    <div class="welcome-section">
        <div class="welcome-icon"><i class="fas fa-heart-pulse"></i></div>
        <h2>MedChat AI</h2>
        <p>مساعدك الطبي الذكي</p>
        <div class="welcome-message">
            <p>
                مرحبًا! أنا <strong>MedChat AI</strong>، مساعدك الطبي الذكي الخاص.<br><br>
                <strong>كيف يمكنني مساعدتك اليوم؟</strong><br><br>
                يمكنك سؤالي عن:<br>
                • الأعراض والمشاكل الصحية<br>
                • الأمراض والحالات الطبية<br>
                • طرق الوقاية والعلاج الآمن<br>
                • نصائح الصحة العامة<br><br>
                <em>تذكير مهم: أنا أقدم معلومات طبية موثوقة فقط، ولست بديلاً عن استشارة طبيب مختص.</em>
            </p>
        </div>
    </div>
`;

// بدء شات جديد تلقائيًا
document.addEventListener("DOMContentLoaded", () => {
    resetChat();
    fetch("/api/new_chat", { method: "POST" })
        .then(() => console.log("جلسة جديدة بدأت"))
        .catch(err => console.error("فشل بدء الجلسة:", err));
});

newChatBtn.addEventListener("click", () => {
    resetChat();
    fetch("/api/new_chat", { method: "POST" }).catch(() => alert("فشل إنشاء شات جديد"));
});

function resetChat() {
    messagesArea.innerHTML = welcomeHTML;
    messageInput.value = "";
    messageInput.focus();
    _isLoading = false;
    sendBtn.disabled = false;
    sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
}

// إضافة رسالة مع أنيميشن وتأثيرات
function addMessage(text, sender, isTyping = false) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message animate__animated animate__fadeInUp`;

    if (isTyping) {
        messageDiv.innerHTML = `
            <div class="typing-bubble">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
                <div class="typing-text">MedChat AI يكتب...</div>
            </div>`;
        messagesArea.appendChild(messageDiv);
        messagesArea.scrollTop = messagesArea.scrollHeight;
        return messageDiv;
    }

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    const formattedText = text
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/```(.*?)```/gs, "<pre class='code-block'>$1</pre>")
        .replace(/`(.*?)`/g, "<code class='inline-code'>$1</code>");

    bubble.innerHTML = formattedText;
    messageDiv.appendChild(bubble);
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;

    // صوت خفيف عند رد الـ AI
    if (sender === "assistant") {
        const beep = new Audio("data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=");
        beep.volume = 0.3;
        beep.play().catch(() => {});
    }

    return messageDiv;
}

// تعديل ارتفاع الـ textarea
function adjustTextareaHeight() {
    messageInput.style.height = "auto";
    messageInput.style.height = (messageInput.scrollHeight) + "px";
}
messageInput.addEventListener("input", adjustTextareaHeight);

// إرسال الرسالة
async function sendMessage() {
    let text = messageInput.value.trim();
    if (!text || _isLoading) return;

    addMessage(text, "user");
    messageInput.value = "";
    adjustTextareaHeight();

    const typingIndicator = addMessage("", "assistant", true);

    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    _isLoading = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        typingIndicator.remove();

        if (data.error) {
            addMessage("تحذير: " + (data.error || "حدث خطأ، حاول مرة أخرى"), "assistant");
        } else {
            addMessage(data.reply, "assistant");
        }
    } catch (err) {
        typingIndicator.remove();
        addMessage("تحذير: لا يمكن الاتصال بالخادم<br>تأكد أن LM Studio شغال وngrok مفتوح", "assistant");
        console.error("Connection Error:", err);
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        _isLoading = false;
    }
}

// إرسال بـ Enter
messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);
messageInput.focus();
