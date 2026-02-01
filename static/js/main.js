// app.js

document.addEventListener('DOMContentLoaded', function () {

    /* =========================
       УВЕДОМЛЕНИЯ
    ========================== */
    function showNotification(message) {
        // удаляем старые уведомления
        document.querySelectorAll('.custom-notification').forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = 'custom-notification';
        notification.innerHTML = `
            <div style="display:flex;align-items:center;gap:8px">
                <span>✔</span>
                <span>${message}</span>
            </div>
        `;

        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #E53935, #FF8C00);
            color: #fff;
            padding: 14px 18px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,.3);
            z-index: 9999;
            animation: slideIn 0.3s ease;
            max-width: 320px;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /* =========================
       КОПИРОВАНИЕ В БУФЕР
    ========================== */
    window.copyReferralLink = function () {
        const input = document.getElementById('referralLink');
        if (!input) return;

        input.select();
        input.setSelectionRange(0, 99999);

        if (navigator.clipboard) {
            navigator.clipboard.writeText(input.value)
                .then(() => showNotification('Ссылка скопирована!'))
                .catch(() => fallbackCopy(input));
        } else {
            fallbackCopy(input);
        }
    };

    function fallbackCopy(input) {
        try {
            document.execCommand('copy');
            showNotification('Ссылка скопирована!');
        } catch (e) {
            console.error('Ошибка копирования:', e);
        }
    }

    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.copyTarget;
            const input = document.getElementById(targetId);
            if (!input) return;
            input.select();
            fallbackCopy(input);
        });
    });

    /* =========================
       ФОРМА РЕГИСТРАЦИИ
    ========================== */
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', e => {
            e.preventDefault();

            const btn = registerForm.querySelector('button[type="submit"]');
            if (!btn) return;

            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '⏳ Регистрация...';

            // имитация AJAX
            setTimeout(() => {
                showNotification('Партнер успешно зарегистрирован!');
                btn.innerHTML = originalText;
                btn.disabled = false;

                if (window.bootstrap) {
                    const modalEl = document.getElementById('registerModal');
                    if (modalEl) {
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        modal && modal.hide();
                    }
                }
            }, 1200);
        });
    }

    /* =========================
       ФИЛЬТРЫ КАТАЛОГА
    ========================== */
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const pageInput = filterForm.querySelector('input[name="page"]');

        filterForm.querySelectorAll('input, select').forEach(el => {
            el.addEventListener('change', () => {
                if (pageInput) pageInput.value = 1;
                filterForm.submit();
            });
        });
    }

    /* =========================
       TOOLTIP BOOTSTRAP
    ========================== */
    if (window.bootstrap) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
            .forEach(el => new bootstrap.Tooltip(el));
    }

    /* =========================
       AUTO-FILL CODE (для теста)
    ========================== */
    window.autoFillCode = function () {
        const input = document.getElementById('{{ form.verification_code.id_for_label|default:"" }}');
        if (input && !input.value) {
            input.value = '123456';
        }
    };
});

/* =========================
   АНИМАЦИИ
========================== */
const style = document.createElement('style');
style.innerHTML = `
@keyframes slideIn {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes slideOut {
    from { opacity: 1; }
    to { opacity: 0; }
}`;
document.head.appendChild(style);
