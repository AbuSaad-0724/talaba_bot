// Library - Backend Integration
const urlParams = new URLSearchParams(window.location.search);
const serverUrl = urlParams.get('server') || '';
const API_BASE = serverUrl ? serverUrl.replace(/\/$/, '') : window.location.origin;

// Fetch materials from backend
async function fetchMaterials(subject = null, level = null, materialType = null) {
    try {
        let url = `${API_BASE}/api/library/materials?`;
        const params = [];

        if (subject) params.push(`subject=${subject}`);
        if (level) params.push(`level=${level}`);
        if (materialType) params.push(`material_type=${materialType}`);

        url += params.join('&');

        const response = await fetch(url, {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        if (!response.ok) throw new Error('Failed to fetch materials');

        const data = await response.json();
        return data.materials || [];
    } catch (error) {
        console.error('Fetch materials error:', error);
        return [];
    }
}

// Get subject statistics
async function fetchSubjectStats(subject) {
    try {
        const response = await fetch(`${API_BASE}/api/library/stats/${subject}`, {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        if (!response.ok) throw new Error('Failed to fetch stats');

        return await response.json();
    } catch (error) {
        console.error('Fetch stats error:', error);
        return {
            total_materials: 0,
            video_count: 0,
            pdf_count: 0,
            audio_count: 0
        };
    }
}

// Get material by ID and increment views
async function getMaterial(materialId) {
    try {
        const response = await fetch(`${API_BASE}/api/library/materials/${materialId}`);
        if (!response.ok) throw new Error('Failed to get material');

        return await response.json();
    } catch (error) {
        console.error('Get material error:', error);
        return null;
    }
}

// Merge backend data with static library data
async function mergeLibraryData() {
    const backendMaterials = await fetchMaterials();

    // Group by subject and level
    const grouped = {};

    backendMaterials.forEach(material => {
        if (!grouped[material.subject]) {
            grouped[material.subject] = {};
        }
        if (!grouped[material.subject][material.level]) {
            grouped[material.subject][material.level] = [];
        }

        grouped[material.subject][material.level].push({
            type: material.material_type,
            title: material.title,
            duration: material.duration,
            url: material.file_url,
            description: material.description,
            id: material.id,
            views: material.views_count
        });
    });

    // Merge with static data
    Object.keys(libraryData).forEach(subjectKey => {
        const subject = libraryData[subjectKey];

        if (grouped[subjectKey]) {
            Object.keys(grouped[subjectKey]).forEach(levelKey => {
                if (subject.levels[levelKey]) {
                    // Append backend materials to existing level
                    subject.levels[levelKey].materials = [
                        ...subject.levels[levelKey].materials,
                        ...grouped[subjectKey][levelKey]
                    ];
                }
            });
        }
    });

    return libraryData;
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fetchMaterials,
        fetchSubjectStats,
        getMaterial,
        mergeLibraryData
    };
}
