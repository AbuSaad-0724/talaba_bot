// Admin Library - Backend Integration
const API_BASE = window.location.origin; // or your backend URL

// Get Telegram user ID
const tg = window.Telegram.WebApp;
const userId = tg.initDataUnsafe?.user?.id || 0;

// Upload file to backend
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    try {
        const response = await fetch(`${API_BASE}/api/library/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');
        return await response.json();
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

// Add material to database
async function addMaterial(materialData) {
    try {
        const response = await fetch(`${API_BASE}/api/library/materials`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...materialData,
                user_id: userId
            })
        });

        if (!response.ok) throw new Error('Failed to add material');
        return await response.json();
    } catch (error) {
        console.error('Add material error:', error);
        throw error;
    }
}

// Get all materials
async function getMaterials() {
    try {
        const response = await fetch(`${API_BASE}/api/library/materials`);
        if (!response.ok) throw new Error('Failed to get materials');
        const data = await response.json();
        return data.materials || [];
    } catch (error) {
        console.error('Get materials error:', error);
        return [];
    }
}

// Delete material
async function deleteMaterial(materialId) {
    try {
        const response = await fetch(`${API_BASE}/api/library/materials/${materialId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });

        if (!response.ok) throw new Error('Failed to delete material');
        return await response.json();
    } catch (error) {
        console.error('Delete material error:', error);
        throw error;
    }
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        uploadFile,
        addMaterial,
        getMaterials,
        deleteMaterial
    };
}
