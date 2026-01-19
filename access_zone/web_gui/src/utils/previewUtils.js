import React from "react";
import {marked} from "marked";
import DOMPurify from "dompurify";
import {downloadObject} from './s3client';
import Papa from "papaparse";
import JSZip from "jszip";
import * as XLSX from "xlsx";
import WaveSurfer from "wavesurfer.js";
import hljs from "highlight.js";
import "highlight.js/styles/vs2015.css";
import {Tree} from "primereact/tree"; // Importer Tree de PrimeReact
import prettyBytes from "pretty-bytes"; // Pour formater la taille des fichiers


// Cache pour les prévisualisations
const previewCache = new Map();

// Composant pour gérer les erreurs
const ErrorPreview = ({error}) => (
    <div className="text-red-500 p-4">
        Impossible de générer la prévisualisation : {error}
    </div>
);

// Composant pour Markdown
const MarkdownPreview = ({content}) => (
    <div
        className="markdown-preview border border-blue-500 p-4"
        dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(marked.parse(content))}}
    />
);

// Composant pour Vidéo
const VideoPreview = ({signedUrl}) => (
    <video className="max-w-full h-auto" width="320" height="240" controls>
        <source src={signedUrl} type="video/mp4"/>
        Votre navigateur ne supporte pas la balise vidéo.
    </video>
);

// Composant pour CSV
const CsvPreview = ({headers, rows}) => (
    <table className="preview-table w-full border-collapse">
        <thead>
        <tr>
            {headers.map((header) => (
                <th key={header} className="preview-table-header border p-2 bg-gray-100">
                    {header}
                </th>
            ))}
        </tr>
        </thead>
        <tbody>
        {rows.map((row, index) => (
            <tr key={index}>
                {headers.map((header) => (
                    <td key={header} className="preview-table-cell border p-2">
                        {row[header] || ""}
                    </td>
                ))}
            </tr>
        ))}
        </tbody>
    </table>
);

// Composant pour Image
const ImagePreview = ({signedUrl}) => (
    <img src={signedUrl} alt="Prévisualisation" className="max-w-full h-auto"/>
);

// Composant pour PDF
const PdfPreview = ({signedUrl}) => (
    <iframe src={signedUrl} className="w-full h-[600px]"/>
);

// Composant pour Excel
const ExcelPreview = ({headers, rows}) => (
    <table className="preview-table w-full border-collapse">
        <thead>
        <tr>
            {headers.map((header) => (
                <th key={header} className="preview-table-header border p-2 bg-gray-100">
                    {header}
                </th>
            ))}
        </tr>
        </thead>
        <tbody>
        {rows.map((row, index) => (
            <tr key={index}>
                {headers.map((header, i) => (
                    <td key={i} className="preview-table-cell border p-2">
                        {row[i] || ""}
                    </td>
                ))}
            </tr>
        ))}
        </tbody>
    </table>
);

// // Composant pour Audio
// const AudioPreview = ({signedUrl, waveContainerRef}) => {
//     React.useEffect(() => {
//         const waveSurfer = WaveSurfer.create({
//             container: waveContainerRef.current,
//             waveColor: "#4a90e2",
//             progressColor: "#50e3c2",
//             height: 100,
//             barWidth: 2,
//             responsive: true,
//         });
//         waveSurfer.load(signedUrl);
//         waveSurfer.on("error", (err) => console.error("Erreur wavesurfer", err));
//         return () => waveSurfer.destroy();
//     }, [signedUrl]);
//
//     return (
//         <div>
//             <div ref={waveContainerRef} className="wave-container"/>
//             <audio controls src={signedUrl}>
//                 Votre navigateur ne supporte pas l'audio.
//             </audio>
//         </div>
//     );
// };
// Composant pour Audio (synchro WaveSurfer + lecteur natif)
const AudioPreview = ({signedUrl}) => {
    const audioRef = React.useRef(null);
    const waveformRef = React.useRef(null);
    const wavesurferRef = React.useRef(null);

    React.useEffect(() => {
        if (!waveformRef.current || !audioRef.current) return;

        const audio = audioRef.current;
        const wavesurfer = WaveSurfer.create({
            container: waveformRef.current,
            waveColor: "#4a90e2",
            progressColor: "#50e3c2",
            height: 100,
            barWidth: 2,
            responsive: true,
            url: signedUrl,  // Charge waveform
            interact: false,
            dragToSeek: true,
            autoCenter: true,
        });

        wavesurferRef.current = wavesurfer;

        // Synchro audio → WaveSurfer (progress, play/pause)
        const syncToWave = () => {
            if (audio.duration) {
                const progress = audio.currentTime / audio.duration;
                wavesurfer.seekTo(progress);
            }
        };

        const handlePlay = () => wavesurfer.play();
        const handlePause = () => wavesurfer.pause();

        audio.addEventListener('timeupdate', syncToWave);
        audio.addEventListener('play', handlePlay);
        audio.addEventListener('pause', handlePause);
        audio.addEventListener('ended', () => wavesurfer.pause());
        wavesurfer.setVolume(0);
        wavesurfer.on('ready', () => {
            wavesurfer.seekTo(audio.currentTime / audio.duration || 0);  // Init position
        });

        // Synchro WaveSurfer → audio (seeking)
        wavesurfer.on('seek', (progress) => {
            if (audio.duration) {
                audio.currentTime = progress * audio.duration;
            }
        });

        wavesurfer.on('play', () => audio.play());
        wavesurfer.on('pause', () => audio.pause());

        wavesurfer.on("error", (err) => console.error("Erreur wavesurfer", err));

        // Cleanup
        return () => {
            audio.removeEventListener('timeupdate', syncToWave);
            audio.removeEventListener('play', handlePlay);
            audio.removeEventListener('pause', handlePause);
            audio.removeEventListener('ended', () => wavesurfer.pause());
            if (wavesurfer) wavesurfer.destroy();
            if (signedUrl.startsWith('blob:')) URL.revokeObjectURL(signedUrl);
        };
    }, [signedUrl]);

    return (
        <div className="audio-preview">
            <div ref={waveformRef} className="wave-container"/>
            <audio
                ref={audioRef}
                src={signedUrl}
                controls
                className="w-full mt-2"
                preload="metadata"  // Charge duration sans full load
            >
                Votre navigateur ne supporte pas l'audio.
            </audio>
        </div>
    );
};

// Fonction pour construire une arborescence à partir d'un fichier ZIP
const buildZipTree = (zip) => {
    const tree = [];
    const folders = {};

    Object.keys(zip.files).forEach((filePath) => {
        const parts = filePath.split("/").filter((p) => p);
        let currentLevel = tree;

        parts.forEach((part, index) => {
            const isFile = index === parts.length - 1 && !zip.files[filePath].dir;
            const key = parts.slice(0, index + 1).join("/");

            let node = currentLevel.find((n) => n.key === key);

            if (!node) {
                node = {
                    key,
                    label: part,
                    icon: isFile ? "pi pi-file" : "pi pi-folder",
                    data: isFile
                        ? {type: "file", size: zip.files[filePath]._data?.uncompressedSize || 0}
                        : {type: "folder"},
                    children: [],
                    className: isFile ? "file-node" : "folder-node", // Ajout de classes pour stylisation
                };
                currentLevel.push(node);
            }

            if (!isFile) {
                currentLevel = node.children;
            }
        });
    });

    return tree;
};


// Composant pour Zip avec arborescence
const ZipPreview = ({treeData}) => {
    const nodeTemplate = (node) => {
        if (node.data.type === "file") {
            return (
                <span>
          {node.label} ({prettyBytes(node.data.size)})
        </span>
            );
        }
        return <span>{node.label}</span>;
    };

    return (
        <div className="p-4">
            <h3>Contenu de l'archive</h3>
            <Tree value={treeData} nodeTemplate={nodeTemplate}/>
        </div>
    );
};
// Composant pour Texte (avec Highlight.js)
const TextPreview = ({content}) => {
    const highlighted = hljs.highlightAuto(content).value;
    return (
        <div className="card border border-blue-500">
            <div className="content">
        <pre style={{
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            maxWidth: "100%",
            overflowX: "auto",
            padding: "1rem"
        }}>
          <code className="language-auto" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(highlighted)}}/>
        </pre>
            </div>
        </div>
    );
};

// Composant par défaut pour les types non supportés
const DefaultPreview = () => (
    <div className="p-4">Prévisualisation non disponible pour ce type de fichier.</div>
);

export const getPreviewContent = async (bucketName, node) => {
    const {key, data} = node;
    console.log("METADATA = ")
    console.log(data)
    const fileType = data["contentType"] || "";
    const cacheKey = `${bucketName}:${key}:${data.lastModified || ""}`;

    if (previewCache.has(cacheKey)) {
        return previewCache.get(cacheKey);
    }

    try {
        // 1. Markdown
        if (fileType === "text/markdown" || key.endsWith(".md")) {
            console.log(" 1. Markdown")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob via proxy
                const mdContent = await blob.text();  // Convert Blob to string
                const result = {component: <MarkdownPreview content={mdContent}/>, error: null, data: null};
                previewCache.set(cacheKey, result);
                return result;
            } catch (err) {
                console.error("Erreur preview Markdown", err);
                return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
            }
        }
        // 2. Vidéo
        else if (fileType.startsWith("video/")) {
            console.log(" 2. Video")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob
                const url = URL.createObjectURL(blob);  // URL locale sécurisée
                const result = {component: <VideoPreview signedUrl={url}/>, error: null, data: null};
                previewCache.set(cacheKey, result);
                // Cleanup : revoke après usage (dans composant VideoPreview useEffect return)
                return result;
            } catch (err) {
                console.error("Erreur preview Vidéo", err);
                return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
            }
        }
        // 3. CSV
        else if (fileType === "text/csv" || key.endsWith(".csv")) {
            console.log(" 3. CSV")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob
                const csvContent = await blob.text();  // Convert to string
                const parsed = Papa.parse(csvContent, {header: true, preview: 10});
                if (parsed.data.length > 0) {
                    const headers = Object.keys(parsed.data[0]);
                    const result = {
                        component: <CsvPreview headers={headers} rows={parsed.data}/>,
                        error: null,
                        data: {headers, rows: parsed.data},
                    };
                    previewCache.set(cacheKey, result);
                    return result;
                } else {
                    throw new Error("Fichier CSV vide ou malformé");
                }
            } catch (err) {
                console.error("Erreur prévisualisation CSV", err);
                return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
            }
        }
        // 4. Image
        else if (fileType.startsWith("image/")) {
            console.log(" 4. Image")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob
                const url = URL.createObjectURL(blob);  // URL locale
                const result = {component: <ImagePreview signedUrl={url}/>, error: null, data: null};
                previewCache.set(cacheKey, result);
                return result;
            } catch (err) {
                console.error("Erreur preview Image", err);
                return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
            }
        }
        // 5. PDF
        else if (fileType === "application/pdf") {
            console.log(" 5. PDF")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob
                const url = URL.createObjectURL(blob);  // URL locale pour iframe
                const result = {component: <PdfPreview signedUrl={url}/>, error: null, data: null};
                previewCache.set(cacheKey, result);
                return result;
            } catch (err) {
                console.error("Erreur preview PDF", err);
                return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
            }
        }
        // 6. Excel


        else if (fileType === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                 fileType === "application/vnd.oasis.opendocument.spreadsheet" ||
                 fileType === 'application/vnd.ms-excel' ||
                 fileType === 'application/vnd.openxmlformatsofficedocument.spreadsheetml.sheet') {
            console.log(" 6. Excel")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob
                const arrayBuffer = await blob.arrayBuffer();  // Convert to ArrayBuffer pour XLSX
                const workbook = XLSX.read(arrayBuffer, {type: "array"});  // type: "array" au lieu "buffer"
                const sheetName = workbook.SheetNames[0];
                const worksheet = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName], {header: 1, range: 5});
                const headers = worksheet[0] || [];
                const result = {
                    component: <ExcelPreview headers={headers} rows={worksheet.slice(1, 6)}/>,
                    error: null,
                    data: null,
                };
                previewCache.set(cacheKey, result);
                return result;
            } catch (err) {
                console.error("Erreur preview Excel", err);
                return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
            }
        }
        // 7. Audio
        else if (fileType.startsWith("audio/")) {
            console.log(" 7. Audio")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob
                const url = URL.createObjectURL(blob);  // URL locale
                const waveContainerRef = React.createRef();
                const result = {
                    component: <AudioPreview signedUrl={url} waveContainerRef={waveContainerRef}/>,
                    error: null,
                    data: null,
                };
                previewCache.set(cacheKey, result);
                return result;
            } catch (err) {
                console.error("Erreur prévisualisation audio", err);
                return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
            }
            // ZIP Archive
        } else if (["application/zip", "application/x-tar", "application/x-zip-compressed"].includes(fileType)) {
            console.log(" 8. ZIP")
            try {
                const blob = await downloadObject(bucketName, key);  // Fetch Blob
                const arrayBuffer = await blob.arrayBuffer();  // Convert to ArrayBuffer
                const archiveData = Buffer.from(arrayBuffer);  // Polyfill Buffer en browser (si besoin ; sinon use Uint8Array)

                if (fileType === "application/zip" || fileType === "application/x-zip-compressed") {
                    const zip = await JSZip.loadAsync(archiveData);
                    const treeData = buildZipTree(zip);
                    const result = {component: <ZipPreview treeData={treeData}/>, error: null, data: null};
                    previewCache.set(cacheKey, result);
                    return result;
                } else if (fileType === "application/x-tar") {
                    const result = {
                        component: <div>Prévisualisation non disponible pour les fichiers TAR.</div>,
                        error: null,
                        data: null,
                    };
                    previewCache.set(cacheKey, result);
                    return result;
                }
            } catch (err) {
                console.error("Erreur preview Zip", err);
                const result = {
                    component: <ErrorPreview error="Erreur lors du chargement de l'archive"/>,
                    error: err.message,
                    data: null,
                };
                previewCache.set(cacheKey, result);
                return result;
            }
        } else {
            console.log(" 9. Default")
            console.log(fileType);
            if (fileType.startsWith("text/")) {
                try {
                    const blob = await downloadObject(bucketName, key);  // Fetch Blob
                    const textContent = await blob.text();  // Convert to string
                    console.log("TA MERE")
                    console.log(textContent);
                    const result = {component: <TextPreview content={textContent}/>, error: null, data: null};
                    previewCache.set(cacheKey, result);
                    return result;
                } catch (err) {
                    console.error("Erreur preview Texte", err);
                    return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
                }
            } else {
                console.log("TA MERE")
                const result = {component: <DefaultPreview/>, error: null, data: null};
                previewCache.set(cacheKey, result);
                return result;
            }
        }
    } catch (err) {
        console.error("Erreur prévisualisation", err);
        return {component: <ErrorPreview error={err.message}/>, error: err.message, data: null};
    } finally {
        if (previewCache.size > 50) {
            const oldestKey = previewCache.keys().next().value;
            previewCache.delete(oldestKey);
        }
        console.log(`Preview cache size: ${previewCache.size}`);  // Debug, supprimez en prod
    }
};