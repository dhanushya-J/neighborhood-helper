// Neighborhood Helper - Main JavaScript Interactions

document.addEventListener('DOMContentLoaded', function () {
    // 1. Notification Dropdown Toggle
    const notifBell = document.getElementById('notifBell');
    const notifMenu = document.getElementById('notifMenu');
    const markReadBtn = document.getElementById('markAllReadBtn');

    if (notifBell && notifMenu) {
        notifBell.addEventListener('click', function (e) {
            e.stopPropagation();
            notifMenu.classList.toggle('show');
        });

        document.addEventListener('click', function (e) {
            if (!notifMenu.contains(e.target) && e.target !== notifBell) {
                notifMenu.classList.remove('show');
            }
        });
    }

    if (markReadBtn) {
        markReadBtn.addEventListener('click', function (e) {
            e.preventDefault();
            fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).then(response => response.json())
              .then(data => {
                  if (data.status === 'success') {
                      const countBadge = document.querySelector('.notif-count');
                      if (countBadge) countBadge.remove();
                      document.querySelectorAll('.notif-item.unread').forEach(item => {
                          item.classList.remove('unread');
                      });
                  }
              }).catch(err => console.log('Notification mark read error:', err));
        });
    }

    // 2. Geolocation "Use My Current Location" feature
    const useLocationBtn = document.getElementById('useGpsBtn');
    const locationInput = document.getElementById('locationInput');
    const latInput = document.getElementById('latInput');
    const lngInput = document.getElementById('lngInput');

    if (useLocationBtn && locationInput) {
        // If user manually types an area name, clear hidden GPS values so the typed locality takes priority
        locationInput.addEventListener('input', function () {
            if (latInput) latInput.value = '';
            if (lngInput) lngInput.value = '';
        });

        useLocationBtn.addEventListener('click', function () {
            if (!navigator.geolocation) {
                alert('Geolocation is not supported by your browser. Please enter your neighborhood area manually.');
                return;
            }

            useLocationBtn.disabled = true;
            useLocationBtn.innerText = 'Detecting...';

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    if (latInput) latInput.value = lat;
                    if (lngInput) lngInput.value = lng;
                    locationInput.value = `Current Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
                    useLocationBtn.disabled = false;
                    useLocationBtn.innerText = '✓ Located';
                    setTimeout(() => { useLocationBtn.innerText = 'Use Current GPS'; }, 3000);
                },
                function (error) {
                    useLocationBtn.disabled = false;
                    useLocationBtn.innerText = 'Use Current GPS';
                    let msg = 'Unable to retrieve location.';
                    if (error.code === error.PERMISSION_DENIED) {
                        msg = 'Location access was denied. You can manually enter your area name (e.g. Anna Nagar, Velachery).';
                    }
                    alert(msg);
                },
                { timeout: 10000, enableHighAccuracy: true }
            );
        });
    }

    // 3. Helper Complete Work Amount Real-Time Calculation
    const serviceAmtInput = document.getElementById('serviceAmountInput');
    const additionalAmtInput = document.getElementById('additionalAmountInput');
    const finalAmtDisplay = document.getElementById('finalAmountDisplay');

    function updateFinalAmount() {
        if (serviceAmtInput && finalAmtDisplay) {
            const base = parseFloat(serviceAmtInput.value) || 0;
            const extra = additionalAmtInput ? (parseFloat(additionalAmtInput.value) || 0) : 0;
            finalAmtDisplay.innerText = '₹' + (base + extra).toFixed(2);
        }
    }

    if (serviceAmtInput) {
        serviceAmtInput.addEventListener('input', updateFinalAmount);
    }
    if (additionalAmtInput) {
        additionalAmtInput.addEventListener('input', updateFinalAmount);
    }

    // 4. Interactive 5-Star Rating Widget
    const starContainer = document.getElementById('interactiveStars');
    const ratingInput = document.getElementById('ratingValueInput');

    if (starContainer && ratingInput) {
        const stars = starContainer.querySelectorAll('.star-icon');
        stars.forEach(star => {
            star.addEventListener('click', function () {
                const val = parseInt(this.getAttribute('data-value'));
                ratingInput.value = val;
                highlightStars(val);
            });
            star.addEventListener('mouseover', function () {
                const val = parseInt(this.getAttribute('data-value'));
                highlightStars(val);
            });
        });

        starContainer.addEventListener('mouseleave', function () {
            highlightStars(parseInt(ratingInput.value) || 5);
        });

        function highlightStars(val) {
            stars.forEach(s => {
                const sVal = parseInt(s.getAttribute('data-value'));
                if (sVal <= val) {
                    s.classList.add('selected');
                } else {
                    s.classList.remove('selected');
                }
            });
        }
    }

    // 5. Payment Method Switcher
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
    const cardFields = document.getElementById('cardFields');
    const upiFields = document.getElementById('upiFields');
    const cashFields = document.getElementById('cashFields');

    if (paymentRadios.length > 0) {
        paymentRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                const method = this.value.toLowerCase();
                if (cardFields) cardFields.style.display = (method === 'card') ? 'block' : 'none';
                if (upiFields) upiFields.style.display = (method === 'upi') ? 'block' : 'none';
                if (cashFields) cashFields.style.display = (method === 'cash') ? 'block' : 'none';

                paymentRadios.forEach(r => {
                    const lbl = r.closest('label');
                    if (lbl) {
                        if (r.checked) {
                            lbl.style.border = '2px solid var(--primary)';
                            lbl.style.background = '#f0f7ff';
                        } else {
                            lbl.style.border = '1px solid var(--border-color)';
                            lbl.style.background = 'transparent';
                        }
                    }
                });
            });
        });
    }
});
