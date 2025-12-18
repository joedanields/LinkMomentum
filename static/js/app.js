// ==================== Application State ====================
let currentEventId = null;
let allImages = [];
let selectedImageCount = 0;
let isAuthenticated = false;

// ==================== DOM Elements ====================
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectFilesBtn = document.getElementById('selectFilesBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const summarySection = document.getElementById('summarySection');
const gallerySection = document.getElementById('gallerySection');
const imageGrid = document.getElementById('imageGrid');
const postSection = document.getElementById('postSection');
const linkedinAuthBtn = document.getElementById('linkedinAuthBtn');
const authStatusBadge = document.getElementById('authStatusBadge');
const authStatusText = document.getElementById('authStatusText');
const postToLinkedInBtn = document.getElementById('postToLinkedInBtn');
const postCaption = document.getElementById('postCaption');
const selectedCount = document.getElementById('selectedCount');
const showAllBtn = document.getElementById('showAllBtn');
const showSelectedBtn = document.getElementById('showSelectedBtn');
const toastContainer = document.getElementById('toastContainer');
const loadingOverlay = document.getElementById('loadingOverlay');

// ==================== Initialize Application ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    await checkAuthStatus();
    await loadStats();
    setupEventListeners();
    checkAuthQueryParam();
}

// ==================== Event Listeners ====================
function setupEventListeners() {
    // Upload area interactions
    selectFilesBtn.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // LinkedIn authentication
    linkedinAuthBtn.addEventListener('click', initiateLinkedInAuth);
    
    // Post to LinkedIn
    postToLinkedInBtn.addEventListener('click', postToLinkedIn);
    
    // Gallery filters
    showAllBtn.addEventListener('click', () => filterImages('all'));
    showSelectedBtn.addEventListener('click', () => filterImages('selected'));
}

// ==================== File Upload Handlers ====================
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    processFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    processFiles(files);
}

async function processFiles(files) {
    if (!files || files.length === 0) {
        showToast('Please select at least one image', 'error');
        return;
    }
    
    if (files.length > 20) {
        showToast('Maximum 20 files allowed', 'error');
        return;
    }
    
    // Validate file types
    const validFiles = Array.from(files).filter(file => 
        file.type.startsWith('image/')
    );
    
    if (validFiles.length === 0) {
        showToast('Please select valid image files', 'error');
        return;
    }
    
    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading images...';
    
    // Create FormData
    const formData = new FormData();
    validFiles.forEach(file => {
        formData.append('files', file);
    });
    
    try {
        // Simulate progress
        animateProgress(0, 30, 500);
        
        // Upload files
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        animateProgress(30, 60, 500);
        progressText.textContent = 'Processing with AI...';
        
        const data = await response.json();
        
        animateProgress(60, 100, 500);
        progressText.textContent = 'Complete!';
        
        // Store event data
        currentEventId = data.event_id;
        allImages = data.images;
        selectedImageCount = data.total_selected;
        
        // Display results
        displaySummary(data.summary);
        displayImages(allImages);
        updateSelectedCount();
        
        // Show sections
        setTimeout(() => {
            summarySection.style.display = 'block';
            gallerySection.style.display = 'block';
            progressContainer.style.display = 'none';
            
            // Scroll to summary
            summarySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 1000);
        
        showToast('Images processed successfully!', 'success');
        
    } catch (error) {
        console.error('Upload error:', error);
        showToast('Failed to upload images. Please try again.', 'error');
        progressContainer.style.display = 'none';
    }
}

function animateProgress(from, to, duration) {
    const start = Date.now();
    const animate = () => {
        const now = Date.now();
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const currentProgress = from + (to - from) * progress;
        
        progressFill.style.width = `${currentProgress}%`;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    animate();
}

// ==================== Display Functions ====================
function displaySummary(summary) {
    document.getElementById('summaryTotal').textContent = summary.total;
    document.getElementById('summaryHighQuality').textContent = summary.high_quality;
    document.getElementById('summaryBlurry').textContent = summary.blurry;
    document.getElementById('summaryDuplicates').textContent = summary.duplicates;
    document.getElementById('summarySelected').textContent = summary.selected;
}

function displayImages(images) {
    imageGrid.innerHTML = '';
    
    images.forEach((image, index) => {
        const imageCard = createImageCard(image, index);
        imageGrid.appendChild(imageCard);
    });
}

function createImageCard(image, index) {
    const card = document.createElement('div');
    card.className = `image-card ${image.is_selected ? 'selected' : ''}`;
    card.dataset.imageIndex = index;
    card.dataset.imageId = image.id || '';
    
    // Build badges
    let badges = '';
    if (image.is_blur) {
        badges += '<span class="badge badge-blur">Blurry</span>';
    }
    if (image.is_duplicate) {
        badges += '<span class="badge badge-duplicate">Duplicate</span>';
    }
    if (image.is_selected) {
        badges += '<span class="badge badge-selected">Selected</span>';
    }
    
    card.innerHTML = `
        <div class="image-wrapper">
            <img src="${image.url}" alt="${image.filename}" loading="lazy">
            <div class="image-overlay"></div>
            ${badges ? `<div class="image-badges">${badges}</div>` : ''}
            <div class="select-checkbox">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </div>
        </div>
        <div class="image-info">
            <div class="image-filename" title="${image.filename}">${image.filename}</div>
            <div class="image-metrics">
                <div class="metric">
                    <span class="metric-label">Quality</span>
                    <span class="metric-value">${Math.round(image.quality_score * 100)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Sharpness</span>
                    <span class="metric-value">${Math.round(image.sharpness_score * 100)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Brightness</span>
                    <span class="metric-value">${Math.round(image.brightness_score * 100)}%</span>
                </div>
            </div>
            <div class="quality-bar">
                <div class="quality-fill" style="width: ${image.quality_score * 100}%"></div>
            </div>
        </div>
    `;
    
    // Add click handler
    card.addEventListener('click', () => toggleImageSelection(index));
    
    return card;
}

async function toggleImageSelection(index) {
    const image = allImages[index];
    
    try {
        // Update on server
        const imageId = image.id || image.db_id || null;
        if (!imageId) throw new Error('Missing image id');

        const response = await fetch(`/api/images/${imageId}/toggle-select`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to toggle selection');
        }
        
        const data = await response.json();
        
        // Update local state
        image.is_selected = data.is_selected;
        selectedImageCount = data.total_selected;
        
        // Update UI
        const card = document.querySelector(`[data-image-index="${index}"]`);
        if (data.is_selected) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
        
        // Update badges
        const badges = card.querySelector('.image-badges');
        if (badges) {
            const selectedBadge = badges.querySelector('.badge-selected');
            if (data.is_selected && !selectedBadge) {
                badges.innerHTML += '<span class="badge badge-selected">Selected</span>';
            } else if (!data.is_selected && selectedBadge) {
                selectedBadge.remove();
            }
        } else if (data.is_selected) {
            const imageWrapper = card.querySelector('.image-wrapper');
            const badgesDiv = document.createElement('div');
            badgesDiv.className = 'image-badges';
            badgesDiv.innerHTML = '<span class="badge badge-selected">Selected</span>';
            imageWrapper.appendChild(badgesDiv);
        }
        
        updateSelectedCount();
        
    } catch (error) {
        console.error('Toggle error:', error);
        showToast('Failed to update selection', 'error');
    }
}

function updateSelectedCount() {
    selectedCount.textContent = selectedImageCount;
    document.getElementById('summarySelected').textContent = selectedImageCount;
    
    // Enable/disable post button
    if (isAuthenticated && selectedImageCount > 0) {
        postToLinkedInBtn.disabled = false;
    } else {
        postToLinkedInBtn.disabled = true;
    }
}

function filterImages(filter) {
    const cards = document.querySelectorAll('.image-card');
    
    cards.forEach(card => {
        if (filter === 'all') {
            card.classList.remove('hidden');
        } else if (filter === 'selected') {
            if (card.classList.contains('selected')) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        }
    });
    
    // Update button states
    if (filter === 'all') {
        showAllBtn.classList.add('btn-primary');
        showAllBtn.classList.remove('btn-secondary');
        showSelectedBtn.classList.add('btn-secondary');
        showSelectedBtn.classList.remove('btn-primary');
    } else {
        showSelectedBtn.classList.add('btn-primary');
        showSelectedBtn.classList.remove('btn-secondary');
        showAllBtn.classList.add('btn-secondary');
        showAllBtn.classList.remove('btn-primary');
    }
}

// ==================== LinkedIn Authentication ====================
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        
        isAuthenticated = data.authenticated;
        
        if (isAuthenticated) {
            authStatusBadge.classList.remove('disconnected');
            authStatusBadge.classList.add('connected');
            authStatusText.textContent = 'Connected';
            linkedinAuthBtn.textContent = 'Reconnect LinkedIn';
        } else {
            authStatusBadge.classList.remove('connected');
            authStatusBadge.classList.add('disconnected');
            authStatusText.textContent = 'Not Connected';
            linkedinAuthBtn.textContent = 'Connect LinkedIn';
        }
        
        updateSelectedCount();
        
    } catch (error) {
        console.error('Auth check error:', error);
    }
}

async function initiateLinkedInAuth() {
    try {
        const response = await fetch('/api/auth/linkedin');
        const data = await response.json();
        
        // Open LinkedIn OAuth in new window
        const width = 600;
        const height = 700;
        const left = (screen.width - width) / 2;
        const top = (screen.height - height) / 2;
        
        window.open(
            data.auth_url,
            'LinkedIn Authentication',
            `width=${width},height=${height},left=${left},top=${top}`
        );
        
        // Poll for authentication completion
        const pollInterval = setInterval(async () => {
            await checkAuthStatus();
            if (isAuthenticated) {
                clearInterval(pollInterval);
                showToast('Successfully connected to LinkedIn!', 'success');
            }
        }, 2000);
        
        // Stop polling after 5 minutes
        setTimeout(() => clearInterval(pollInterval), 300000);
        
    } catch (error) {
        console.error('LinkedIn auth error:', error);
        showToast('Failed to initiate LinkedIn authentication', 'error');
    }
}

function checkAuthQueryParam() {
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get('auth');
    
    if (authStatus === 'success') {
        showToast('Successfully connected to LinkedIn!', 'success');
        checkAuthStatus();
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authStatus === 'error') {
        showToast('LinkedIn authentication failed', 'error');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ==================== Post to LinkedIn ====================
async function postToLinkedIn() {
    if (!isAuthenticated) {
        showToast('Please connect to LinkedIn first', 'error');
        return;
    }
    
    if (selectedImageCount === 0) {
        showToast('Please select at least one image', 'error');
        return;
    }
    
    if (!currentEventId) {
        showToast('No event data available', 'error');
        return;
    }
    
    const caption = postCaption.value.trim();
    
    // Show loading overlay
    loadingOverlay.style.display = 'flex';
    
    try {
        const response = await fetch(`/api/post/linkedin/${currentEventId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                caption: caption || null
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to post to LinkedIn');
        }
        
        const data = await response.json();
        
        loadingOverlay.style.display = 'none';
        
        showToast(`Successfully posted ${data.num_images} image(s) to LinkedIn!`, 'success');
        
        // Mark images as posted
        allImages.forEach(img => {
            if (img.is_selected) {
                img.is_posted = true;
            }
        });
        
        // Clear caption
        postCaption.value = '';
        
        // Reload stats
        await loadStats();
        
    } catch (error) {
        console.error('Post error:', error);
        loadingOverlay.style.display = 'none';
        showToast(error.message || 'Failed to post to LinkedIn', 'error');
    }
}

// ==================== Statistics ====================
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('totalEvents').textContent = data.total_events;
        document.getElementById('totalImages').textContent = data.total_images_processed;
        document.getElementById('totalPosts').textContent = data.total_posts;
        
    } catch (error) {
        console.error('Stats error:', error);
    }
}

// ==================== Toast Notifications ====================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        error: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        info: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };
    
    toast.innerHTML = `
        ${icons[type] || icons.info}
        <div class="toast-message">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ==================== Utility Functions ====================
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
