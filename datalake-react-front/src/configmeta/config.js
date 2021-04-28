export const config = {
    "types": [
        {
            "id": 0,
            "label": "Veuillez choisir votre type de métadonnée ...",
            "metadonnees": [
            ]
        },
        {
            "id": 1,
            "label": "Météo",
            "metadonnees": [
                {
                    "label": "Métadonnée 1",
                    "type": "text",
                    "id": "meta1",
                    "useState": "useMeta1"
                },
                {
                    "label": "Métadonnée 2",
                    "type": "text",
                    "id": "meta2",
                    "useState": "useMeta2"
                }
            ]
        },
        {
            "id": 2,
            "label": "Capteur",
            "metadonnees": [
                {
                    "label": "Métadonnée 1",
                    "type": "textarea",
                    "id": "meta1",
                    "useState": "useMeta1"
                },
                {
                    "label": "Métadonnée 2",
                    "type": "text",
                    "id": "meta2",
                    "useState": "useMeta2"
                },
                {
                    "label": "Métadonnée 3",
                    "type": "number",
                    "id": "meta3",
                    "useState": "useMeta3"
                }
            ]
        },
        {
            "id": 3,
            "label": "Autre métadonnée",
            "metadonnees": [
                {
                    "label": "Métadonnée 1",
                    "type": "textarea",
                    "id": "meta1",
                    "useState": "useMeta1"
                }
            ]
        }
    ]
}