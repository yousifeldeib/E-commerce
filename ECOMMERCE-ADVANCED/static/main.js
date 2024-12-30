let favorites = [];
let cart = [];
let isDarkMode = localStorage.getItem('darkMode') === 'true';

window.onload = function () {
  if (isDarkMode) {
    document.body.classList.add('dark-mode');
  } else {
    document.body.classList.remove('dark-mode');
  }
  loadCartFromStorage();
};

function toggleTheme() {
  document.body.classList.toggle('dark-mode');
  const button = document.querySelector('.btn-dark');
  if (document.body.classList.contains('dark-mode')) {
    button.textContent = 'Light Mode';
    localStorage.setItem('darkMode', 'true');
  } else {
    button.textContent = 'Dark Mode';
    localStorage.setItem('darkMode', 'false');
  }
}

function addToFavorites(productName, productPrice, productImage) {
  const product = { name: productName, price: productPrice, image: productImage };
  favorites.push(product);
  console.log(favorites);
}

function addToCart(productId, productName, productPrice, productImage) {
  const existingProduct = cart.find((item) => item.id === productId);
  if (existingProduct) {
    existingProduct.quantity += 1;
  } else {
    cart.push({ id: productId, name: productName, price: productPrice, image: productImage, quantity: 1 });
  }
  updateCartSummary();
  updateCartHeader();
  localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartSummary() {
  const cartItemsContainer = document.getElementById('cart-items');
  const cartTotalContainer = document.getElementById('cart-total');
  
  cartItemsContainer.innerHTML = '';

  let total = 0;

  cart.forEach((item) => {
    total += item.price * item.quantity;

    const li = document.createElement('li');
    li.innerHTML = `
      <span>${item.name} (x${item.quantity})</span>
      <span>$${(item.price * item.quantity).toFixed(2)}</span>
      <button onclick="removeFromCart(${item.id})">Remove</button>
    `;
    cartItemsContainer.appendChild(li);
  });

  cartTotalContainer.textContent = total.toFixed(2);
}

function updateCartHeader() {
  const cartHeaderContainer = document.getElementById('cart-header-items');
  const cartItemCount = cart.reduce((total, item) => total + item.quantity, 0);
  cartHeaderContainer.textContent = '${cartItemCount} items';
}

function removeFromCart(productId) {
  const productIndex = cart.findIndex((item) => item.id === productId);
  if (productIndex > -1) {
    cart.splice(productIndex, 1); 
    updateCartSummary();
    updateCartHeader();
  }

  localStorage.setItem('cart', JSON.stringify(cart));
}

function proceedToCheckout() {
  if (cart.length === 0) {
    alert('Your cart is empty!');
    return;
  }
  localStorage.setItem('cart', JSON.stringify(cart));

  window.location.href = '/cart';
}

function displayCartItems() {
  const cartItemsContainer = document.getElementById('cart-items');
  const cartTotalContainer = document.getElementById('cart-total');
  
  cartItemsContainer.innerHTML = '';

  let total = 0;

  cart.forEach((item) => {
    total += item.price * item.quantity;

    const li = document.createElement('li');
    li.innerHTML = `
      <img src="${item.image}" alt="${item.name}" width="50">
      <span>${item.name} (x${item.quantity})</span>
      <span>$${(item.price * item.quantity).toFixed(2)}</span>
    `;
    cartItemsContainer.appendChild(li);
  });

  cartTotalContainer.textContent = total.toFixed(2);
}

function loadCartFromStorage() {
  const storedCart = localStorage.getItem('cart');
  if (storedCart) {
    cart = JSON.parse(storedCart);
    updateCartSummary();
    updateCartHeader();
  }
}
