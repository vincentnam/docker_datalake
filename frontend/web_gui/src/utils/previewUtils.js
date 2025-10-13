import React from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";
import mc from "./mc";
import Papa from "papaparse";
import JSZip from "jszip";
import * as XLSX from "xlsx";
import WaveSurfer from "wavesurfer.js";
import hljs from "highlight.js";
import "highlight.js/styles/vs2015.css";
import { Tree } from "primereact/tree"; // Importer Tree de PrimeReact
import prettyBytes from "pretty-bytes"; // Pour formater la taille des fichiers



// Cache pour les prévisualisations
const previewCache = new Map();

// Composant pour gérer les erreurs
const ErrorPreview = ({ error }) => (
  <div className="text-red-500 p-4">
    Impossible de générer la prévisualisation : {error}
  </div>
);

// Composant pour Markdown
const MarkdownPreview = ({ content }) => (
  <div
    className="markdown-preview border border-blue-500 p-4"
    dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(content)) }}
  />
);

// Composant pour Vidéo
const VideoPreview = ({ signedUrl }) => (
  <video className="max-w-full h-auto" width="320" height="240" controls>
    <source src={signedUrl} type="video/mp4" />
    Votre navigateur ne supporte pas la balise vidéo.
  </video>
);

// Composant pour CSV
const CsvPreview = ({ headers, rows }) => (
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
const ImagePreview = ({ signedUrl }) => (
  <img src={signedUrl} alt="Prévisualisation" className="max-w-full h-auto" />
);

// Composant pour PDF
const PdfPreview = ({ signedUrl }) => (
  <iframe src={signedUrl} className="w-full h-[600px]" />
);

// Composant pour Excel
const ExcelPreview = ({ headers, rows }) => (
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

// Composant pour Audio
const AudioPreview = ({ signedUrl, waveContainerRef }) => {
  React.useEffect(() => {
    const waveSurfer = WaveSurfer.create({
      container: waveContainerRef.current,
      waveColor: "#4a90e2",
      progressColor: "#50e3c2",
      height: 100,
      barWidth: 2,
      responsive: true,
    });
    waveSurfer.load(signedUrl);
    waveSurfer.on("error", (err) => console.error("Erreur wavesurfer", err));
    return () => waveSurfer.destroy();
  }, [signedUrl]);

  return (
    <div>
      <div ref={waveContainerRef} className="wave-container" />
      <audio controls src={signedUrl}>
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
            ? { type: "file", size: zip.files[filePath]._data?.uncompressedSize || 0 }
            : { type: "folder" },
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
const ZipPreview = ({ treeData }) => {
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
      <Tree value={treeData} nodeTemplate={nodeTemplate} />
    </div>
  );
};
// Composant pour Texte (avec Highlight.js)
const TextPreview = ({ content }) => {
  const highlighted = hljs.highlightAuto(content).value;
  return (
    <div className="card border border-blue-500">
      <div className="content">
        <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", maxWidth: "100%", overflowX: "auto", padding: "1rem" }}>
          <code className="language-auto" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(highlighted) }} />
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
  const { key, data } = node;
  const fileType = data.metadata?.["content-type"] || "";
  const cacheKey = `${bucketName}:${key}:${data.lastModified || ""}`;

  if (previewCache.has(cacheKey)) {
    return previewCache.get(cacheKey);
  }

  try {
    // 1. Markdown
    if (fileType === "text/markdown" || key.endsWith(".md")) {
      const streamChunksBuf = [];
      const dataStream = await new Promise((resolve, reject) => {
        mc.getObject(bucketName, key, (err, stream) => {
          if (err) reject(err);
          else resolve(stream);
        });
      });
      dataStream.on("data", (chunk) => streamChunksBuf.push(Buffer.from(chunk)));
      const mdContent = await new Promise((resolve) => {
        dataStream.on("end", () => resolve(Buffer.concat(streamChunksBuf).toString()));
      });
      const result = { component: <MarkdownPreview content={mdContent} />, error: null, data: null };
      previewCache.set(cacheKey, result);
      return result;
    }
    // 2. Vidéo
    else if (fileType.startsWith("video/")) {
      const signedUrl = await mc.presignedGetObject(bucketName, key, 60);
      const result = { component: <VideoPreview signedUrl={signedUrl} />, error: null, data: null };
      previewCache.set(cacheKey, result);
      return result;
    }
    // 3. CSV
    else if (fileType === "text/csv" || key.endsWith(".csv")) {
      try {
        const streamChunksBuf = [];
        const dataStream = await new Promise((resolve, reject) => {
          mc.getObject(bucketName, key, (err, stream) => {
            if (err) reject(err);
            else resolve(stream);
          });
        });
        dataStream.on("data", (chunk) => streamChunksBuf.push(Buffer.from(chunk)));
        const csvContent = await new Promise((resolve) => {
          dataStream.on("end", () => resolve(Buffer.concat(streamChunksBuf).toString()));
        });
        const parsed = Papa.parse(csvContent, { header: true, preview: 10 });
        if (parsed.data.length > 0) {
          const headers = Object.keys(parsed.data[0]);
          const result = {
            component: <CsvPreview headers={headers} rows={parsed.data} />,
            error: null,
            data: { headers, rows: parsed.data },
          };
          previewCache.set(cacheKey, result);
          return result;
        }
      } catch (err) {
        console.error("Erreur prévisualisation CSV", err);
        return { component: <ErrorPreview error={err.message} />, error: err.message, data: null };
      }
    }
    // 4. Image
    else if (fileType.startsWith("image/")) {
      const signedUrl = await mc.presignedGetObject(bucketName, key, 60);
      const result = { component: <ImagePreview signedUrl={signedUrl} />, error: null, data: null };
      previewCache.set(cacheKey, result);
      return result;
    }
    // 5. PDF
    else if (fileType === "application/pdf") {
      const signedUrl = await mc.presignedGetObject(bucketName, key, 60);
      const result = { component: <PdfPreview signedUrl={signedUrl} />, error: null, data: null };
      previewCache.set(cacheKey, result);
      return result;
    }
    // 6. Excel
    else if (fileType === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") {
      const streamChunksBuf = [];
      const dataStream = await new Promise((resolve, reject) => {
        mc.getObject(bucketName, key, (err, stream) => {
          if (err) reject(err);
          else resolve(stream);
        });
      });
      dataStream.on("data", (chunk) => streamChunksBuf.push(Buffer.from(chunk)));
      const xlsxContent = await new Promise((resolve) => {
        dataStream.on("end", () => resolve(Buffer.concat(streamChunksBuf)));
      });
      const workbook = XLSX.read(xlsxContent, { type: "buffer" });
      const sheetName = workbook.SheetNames[0];
      const worksheet = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName], { header: 1, range: 5 });
      const headers = worksheet[0] || [];
      const result = {
        component: <ExcelPreview headers={headers} rows={worksheet.slice(1, 6)} />,
        error: null,
        data: null,
      };
      previewCache.set(cacheKey, result);
      return result;
    }
    // 7. Audio
    else if (fileType.startsWith("audio/")) {
      try {
        const signedUrl = await mc.presignedGetObject(bucketName, key, 60);
        const waveContainerRef = React.createRef();
        const result = {
          component: <AudioPreview signedUrl={signedUrl} waveContainerRef={waveContainerRef} />,
          error: null,
          data: null,
        };
        previewCache.set(cacheKey, result);
        return result;
      } catch (err) {
        console.error("Erreur prévisualisation audio", err);
        return { component: <ErrorPreview error={err.message} />, error: err.message, data: null };
      }
    }
    // 8. Zip/Tar
    // 8. Zip/Tar
    else if (["application/zip", "application/x-tar", "application/x-zip-compressed"].includes(fileType)) {
      const streamChunksBuf = [];
      const dataStream = await new Promise((resolve, reject) => {
        mc.getObject(bucketName, key, (err, stream) => {
          if (err) reject(err);
          else resolve(stream);
        });
      });
      dataStream.on("data", (chunk) => streamChunksBuf.push(Buffer.from(chunk)));
      const archiveData = await new Promise((resolve) => {
        dataStream.on("end", () => resolve(Buffer.concat(streamChunksBuf)));
      });

      if (fileType === "application/zip" || fileType === "application/x-zip-compressed") {
        try {
          const zip = await JSZip.loadAsync(archiveData);
          const treeData = buildZipTree(zip);
          const result = { component: <ZipPreview treeData={treeData} />, error: null, data: null };
          previewCache.set(cacheKey, result);
          return result;
        } catch (err) {
          const result = {
            component: <ErrorPreview error="Erreur lors du chargement de l'archive ZIP" />,
            error: err.message,
            data: null,
          };
          previewCache.set(cacheKey, result);
          return result;
        }
      } else if (fileType === "application/x-tar") {
        const result = {
          component: <div>Prévisualisation non disponible pour les fichiers TAR.</div>,
          error: null,
          data: null,
        };
        previewCache.set(cacheKey, result);
        return result;
      }
    }
        /*else if (["application/zip", "application/x-tar"].includes(fileType)) {
      const streamChunksBuf = [];
      const dataStream = await new Promise((resolve, reject) => {
        mc.getObject(bucketName, key, (err, stream) => {
          if (err) reject(err);
          else resolve(stream);
        });
      });
      dataStream.on("data", (chunk) => streamChunksBuf.push(Buffer.from(chunk)));
      const zipData = await new Promise((resolve) => {
        dataStream.on("end", () => resolve(Buffer.concat(streamChunksBuf)));
      });
      const zip = await JSZip.loadAsync(zipData);
      const fileList = Object.keys(zip.files).join(", ");
      const result = { component: <ZipPreview fileList={fileList} />, error: null, data: null };
      previewCache.set(cacheKey, result);
      return result;
    }*/
    // 9. Default (y compris texte)
    else {
      if (fileType.startsWith("text/")) {
        const streamChunksBuf = [];
        const dataStream = await new Promise((resolve, reject) => {
          mc.getObject(bucketName, key, (err, stream) => {
            if (err) reject(err);
            else resolve(stream);
          });
        });
        dataStream.on("data", (chunk) => streamChunksBuf.push(Buffer.from(chunk)));
        const textContent = await new Promise((resolve) => {
          dataStream.on("end", () => resolve(Buffer.concat(streamChunksBuf).toString()));
        });
        const result = { component: <TextPreview content={textContent} />, error: null, data: null };
        previewCache.set(cacheKey, result);
        return result;
      } else {
        const result = { component: <DefaultPreview />, error: null, data: null };
        previewCache.set(cacheKey, result);
        return result;
      }
    }
  } catch (err) {
    console.error("Erreur prévisualisation", err);
    return { component: <ErrorPreview error={err.message} />, error: err.message, data: null };
  } finally {
    if (previewCache.size > 50) {
      const oldestKey = previewCache.keys().next().value;
      previewCache.delete(oldestKey);
    }
  }
};