export const config = {
    "types": [
        {
            "id": 0,
            "label": "Sélectionnez un type de fichier",
            "type_file_accepted": [],
            "metadonnees": [
            ]
        },
        {
            "id": 1,
            "label": "Texte / CSV / Dump SQL",
            "type_file_accepted": ["text/plain", "application/csv", "application/vnd.ms-excel", "application/sql"],
        },
        {
            "id": 2,
            "label": "Image",
            "type_file_accepted": ["image/png", "image/jpeg"],
        },
        {
            "id": 3,
            "label": "Son",
            "type_file_accepted": [],
        },
        {
            "id": 4,
            "label": "Vidéo",
            "type_file_accepted": [],
        },
        {
            "id": 5,
            "label": "Arbre(JSON)",
            "type_file_accepted": ["application/json"],
        },
        {
            "id": 6,
            "label": "Archive",
            "type_file_accepted": ["application/x-zip-compressed", "application/x-gzip"],
        },
        {
            "id": 7,
            "label": "Fichier données SGE",
            "type_file_accepted": ["application/octet-stream"],
        }
    ]
}