// Mesajları otomatik kapat
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });

    // Datetime-local alanlarına şimdiki zamanı varsayılan yap
    document.querySelectorAll('input[type="datetime-local"]').forEach(input => {
        if (!input.value) {
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            input.value = now.toISOString().slice(0, 16);
        }
    });
});
