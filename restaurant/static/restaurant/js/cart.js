/**
 * Smart Restaurant Food Ordering - Dynamic Shopping Cart & UI Controller
 */

// Utility: get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken') || (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '');

// Show Toast notification
function showNotification(message, type = 'success') {
  const toastContainer = document.getElementById('toast-notification-area');
  if (!toastContainer) return;

  const icon = type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-exclamation-triangle-fill text-warning';
  const toastHtml = `
    <div class="toast toast-custom align-items-center show mb-2" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${icon} fs-5"></i>
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = toastHtml;
  const toastElement = tempDiv.firstElementChild;
  toastContainer.appendChild(toastElement);

  setTimeout(() => {
    toastElement.classList.remove('show');
    setTimeout(() => toastElement.remove(), 400);
  }, 3500);
}

// LocalStorage helpers
const LOCAL_STORAGE_KEY = 'restaurant_cart_dimpu';

function getLocalCart() {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function setLocalCart(cart) {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(cart));
}

// Update badges and summary
function updateHeaderCartBadges(count, total) {
  document.querySelectorAll('.cart-count-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'inline-flex' : 'none';
  });
  document.querySelectorAll('.cart-total-display').forEach(el => {
    el.textContent = `$${parseFloat(total || 0).toFixed(2)}`;
  });
}

// Add item to cart
async function addToCart(itemId, quantity = 1, itemName = 'Item') {
  try {
    const response = await fetch('/cart/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({ item_id: itemId, quantity: quantity }),
    });

    const data = await response.json();
    if (data.success) {
      // Update local storage
      const local = getLocalCart();
      local[itemId] = (local[itemId] || 0) + quantity;
      setLocalCart(local);

      updateHeaderCartBadges(data.item_count, data.total_amount);
      showNotification(`Added ${quantity}x <strong>${data.item_name || itemName}</strong> to order!`);
      
      // Update cart drawer if present
      renderDrawerCart();
    } else {
      showNotification(data.error || 'Could not add item to cart', 'warning');
    }
  } catch (err) {
    console.error('Add to cart failed:', err);
    showNotification('Network error while adding item', 'warning');
  }
}

// Update cart quantity in Cart review page
async function updateCartItemQuantity(itemId, newQty) {
  try {
    const response = await fetch('/cart/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({ item_id: itemId, quantity: newQty }),
    });

    const data = await response.json();
    if (data.success) {
      // Update local storage
      const local = getLocalCart();
      if (newQty <= 0) {
        delete local[itemId];
      } else {
        local[itemId] = newQty;
      }
      setLocalCart(local);

      // Reload cart view to show fresh server calculated subtotal & items
      window.location.reload();
    }
  } catch (err) {
    console.error('Update quantity error:', err);
  }
}

// Clear cart
async function clearEntireCart() {
  if (!confirm('Are you sure you want to clear all items from your order?')) return;
  try {
    const response = await fetch('/cart/clear/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
    });
    const data = await response.json();
    if (data.success) {
      localStorage.removeItem(LOCAL_STORAGE_KEY);
      window.location.href = '/';
    }
  } catch (e) {
    window.location.href = '/cart/';
  }
}

// Fetch session cart content for offcanvas drawer
async function renderDrawerCart() {
  const drawerBody = document.getElementById('drawer-cart-items');
  const drawerTotal = document.getElementById('drawer-cart-total');
  const drawerTax = document.getElementById('drawer-cart-tax');
  const drawerSubtotal = document.getElementById('drawer-cart-subtotal');
  const drawerEmpty = document.getElementById('drawer-cart-empty');
  const drawerFooter = document.getElementById('drawer-cart-footer');

  if (!drawerBody) return;

  try {
    // Sync with server session
    const response = await fetch('/cart/sync/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({ cart: getLocalCart() }),
    });
    const data = await response.json();

    if (data.success) {
      updateHeaderCartBadges(data.item_count, data.total_amount);

      if (data.items.length === 0) {
        drawerBody.innerHTML = '';
        if (drawerEmpty) drawerEmpty.style.display = 'block';
        if (drawerFooter) drawerFooter.style.display = 'none';
        return;
      }

      if (drawerEmpty) drawerEmpty.style.display = 'none';
      if (drawerFooter) drawerFooter.style.display = 'block';

      drawerBody.innerHTML = data.items.map(item => `
        <div class="d-flex align-items-center justify-content-between p-2 mb-2 rounded" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle);">
          <div class="d-flex align-items-center gap-2">
            <img src="${item.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=100'}" alt="${item.name}" style="width: 44px; height: 44px; object-fit: cover; border-radius: 8px;">
            <div>
              <div class="fw-bold small text-white">${item.name}</div>
              <div class="text-muted small">$${parseFloat(item.price).toFixed(2)} × ${item.quantity}</div>
            </div>
          </div>
          <div class="text-end">
            <div class="fw-bold text-amber">$${parseFloat(item.subtotal).toFixed(2)}</div>
            <button class="btn btn-sm text-danger p-0 border-0" onclick="updateCartItemQuantity(${item.id}, 0)">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      `).join('');

      if (drawerSubtotal) drawerSubtotal.textContent = `$${data.subtotal}`;
      if (drawerTax) drawerTax.textContent = `$${data.tax_amount}`;
      if (drawerTotal) drawerTotal.textContent = `$${data.total_amount}`;
    }
  } catch (err) {
    console.warn('Could not refresh cart drawer:', err);
  }
}

// Client-side quick filter & search
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-food-input');
  const vegFilterToggle = document.getElementById('veg-filter-toggle');

  function filterCards() {
    const q = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const vegOnly = vegFilterToggle ? vegFilterToggle.checked : false;

    const cards = document.querySelectorAll('.food-item-col');
    let visibleCount = 0;

    cards.forEach(card => {
      const name = (card.getAttribute('data-name') || '').toLowerCase();
      const desc = (card.getAttribute('data-desc') || '').toLowerCase();
      const isVeg = card.getAttribute('data-veg') === 'true';

      const matchesText = !q || name.includes(q) || desc.includes(q);
      const matchesVeg = !vegOnly || isVeg;

      if (matchesText && matchesVeg) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    // Toggle empty message
    const emptyNotice = document.getElementById('no-items-matched');
    if (emptyNotice) {
      emptyNotice.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterCards);
  }
  if (vegFilterToggle) {
    vegFilterToggle.addEventListener('change', filterCards);
  }

  // Populate hidden cart_json input on checkout page if available
  const cartJsonInput = document.getElementById('id_cart_json');
  if (cartJsonInput) {
    cartJsonInput.value = JSON.stringify(getLocalCart());
  }

  // Initial cart sync
  renderDrawerCart();
});
