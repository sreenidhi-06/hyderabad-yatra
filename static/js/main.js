/* ═══════════════════════════════════════════════════════
   HYDERABAD YATRA — Main JavaScript
   ═══════════════════════════════════════════════════════ */

// ─── NAVBAR SCROLL ──────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
});

// ─── MOBILE NAV TOGGLE ──────────────────────────────────
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
if (navToggle) {
    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
}

// ─── USER DROPDOWN ──────────────────────────────────────
const userBtn = document.getElementById('userBtn');
const userDropdown = document.getElementById('userDropdown');
if (userBtn && userDropdown) {
    userBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
        if (!userDropdown.contains(e.target) && !userBtn.contains(e.target)) {
            userDropdown.classList.remove('open');
        }
    });
}

// ─── SCROLL ANIMATIONS ─────────────────────────────────
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.place-card, .food-card, .hotel-card, .budget-card').forEach(el => {
    observer.observe(el);
});

// ─── FILTERS ────────────────────────────────────────────
function filterPlaces(category) {
    const url = new URL(window.location);
    url.searchParams.set('category', category);
    window.location = url;
}
function filterFood(cuisine) {
    const url = new URL(window.location);
    url.searchParams.set('cuisine', cuisine);
    window.location = url;
}
function filterDiet(diet) {
    const url = new URL(window.location);
    url.searchParams.set('diet', diet);
    window.location = url;
}
function filterHotels(budget) {
    const url = new URL(window.location);
    url.searchParams.set('budget', budget);
    window.location = url;
}

// ─── SEARCH ─────────────────────────────────────────────
function searchPlaces(event) {
    if (event.key === 'Enter') {
        const url = new URL(window.location);
        url.searchParams.set('search', event.target.value);
        window.location = url;
    }
}
function searchTransport(event) {
    if (event.key === 'Enter') {
        const url = new URL(window.location);
        url.searchParams.set('search', event.target.value);
        window.location = url;
    }
}

// ─── RECOMMENDATION ENGINE ──────────────────────────────
async function getRecommendations() {
    const interest = document.getElementById('interest')?.value || 'all';
    const budget = document.getElementById('budgetLevel')?.value || 'medium';
    const diet = document.getElementById('dietPref')?.value || 'both';
    const resultsDiv = document.getElementById('recommendResults');
    if (!resultsDiv) return;

    resultsDiv.innerHTML = '<p style="text-align:center;color:#6B6B80;padding:40px;">Loading recommendations...</p>';

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ interest, budget, diet })
        });
        const data = await response.json();
        let html = '';

        if (data.places.length) {
            html += '<h3 style="margin-bottom:16px;color:#6B1D2A;">🏛️ Recommended Places</h3><div class="card-grid" style="margin-bottom:40px;">';
            data.places.forEach(p => {
                html += `<a href="/place/${p.id}" class="place-card"><div class="card-image"><img src="${p.image_url}" alt="${p.name}" onerror="this.src='https://images.unsplash.com/photo-1590766940554-634855926788?w=600'"><span class="card-badge ${p.category==='temple'?'badge-temple':'badge-attraction'}">${p.category}</span></div><div class="card-body"><h3>${p.name}</h3><p>${p.description}</p><div class="card-meta"><span><i class="fas fa-star"></i> ${p.rating}</span><span class="view-btn">View Details →</span></div></div></a>`;
            });
            html += '</div>';
        }
        if (data.food.length) {
            html += '<h3 style="margin-bottom:16px;color:#6B1D2A;">🍽️ Recommended Food</h3><div class="card-grid" style="margin-bottom:40px;">';
            data.food.forEach(f => {
                html += `<div class="food-card"><div class="card-image"><img src="${f.image_url}" alt="${f.name}" onerror="this.src='https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600'"><span class="price-tag">${f.price_range}</span></div><div class="card-body"><h3>${f.name}</h3><p>${f.specialty}</p><div class="card-meta"><span><i class="fas fa-star"></i> ${f.rating}</span><span><i class="fas fa-map-marker-alt"></i> ${f.address}</span></div></div></div>`;
            });
            html += '</div>';
        }
        if (data.hotels.length) {
            html += '<h3 style="margin-bottom:16px;color:#6B1D2A;">🏨 Recommended Hotels</h3><div class="card-grid">';
            data.hotels.forEach(h => {
                html += `<div class="hotel-card"><div class="card-image"><img src="${h.image_url}" alt="${h.name}" onerror="this.src='https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600'"><span class="price-tag">₹${h.price_per_night}/night</span></div><div class="card-body"><h3>${h.name}</h3><p>${h.amenities}</p><div class="card-meta"><span><i class="fas fa-star"></i> ${h.rating}</span><span>${h.category}</span></div></div></div>`;
            });
            html += '</div>';
        }
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = '<p style="text-align:center;color:#C62828;">Error loading recommendations.</p>';
    }
}
