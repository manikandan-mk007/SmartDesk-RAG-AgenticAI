import { useEffect, useMemo, useRef, useState } from "react";
import {
  deleteKBDocument,
  getKBDocuments,
  uploadKBDocument,
} from "../../api/adminApi";
import Card from "../../components/common/Card";
import Icon from "../../components/common/Icon";
import { formatDateTime } from "../../utils/formatDate";

function getDocumentName(doc) {
  return (
    doc.file_name ||
    doc.original_filename ||
    doc.title ||
    `Document-${doc.id}`
  );
}

function getDocumentType(doc) {
  const type = String(doc.file_type || "").toUpperCase();

  if (type) return `${type} Document`;

  const name = getDocumentName(doc).toLowerCase();

  if (name.endsWith(".pdf")) return "PDF Document";
  if (name.endsWith(".md")) return "Markdown";
  if (name.endsWith(".txt")) return "Text Document";
  if (name.endsWith(".docx")) return "DOCX Document";

  return "KB Document";
}

function getStatusClass(status) {
  const value = String(status || "").toUpperCase();

  if (value === "COMPLETED" || value === "SUCCESS") return "success";
  if (value === "PROCESSING" || value === "PENDING") return "processing";
  if (value === "FAILED" || value === "ERROR") return "failed";

  return "processing";
}

function getStatusText(status) {
  const value = String(status || "").toUpperCase();

  if (value === "COMPLETED") return "Success";
  if (value === "PROCESSING") return "Processing";
  if (value === "PENDING") return "Processing";
  if (value === "FAILED") return "Failed";

  return value || "Processing";
}

export default function KBManagementPage() {
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState("");
  const [uploading, setUploading] = useState(false);

  const fileInputRef = useRef(null);

  const loadDocuments = async () => {
    const response = await getKBDocuments();
    setDocuments(response.data);
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUploadFile = async (file) => {
    if (!file) return;

    try {
      setUploading(true);
      const title = file.name.replace(/\.[^/.]+$/, "");
      await uploadKBDocument(title, file);
      await loadDocuments();
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];

    await handleUploadFile(file);

    event.target.value = "";
  };

  const handleDrop = async (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files?.[0];
    await handleUploadFile(file);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this KB document?")) return;

    await deleteKBDocument(id);
    await loadDocuments();
  };

  const filteredDocuments = useMemo(() => {
    const keyword = search.trim().toLowerCase();

    if (!keyword) return documents;

    return documents.filter((doc) => {
      const name = getDocumentName(doc).toLowerCase();
      const type = getDocumentType(doc).toLowerCase();
      const status = String(doc.status || "").toLowerCase();

      return (
        name.includes(keyword) ||
        type.includes(keyword) ||
        status.includes(keyword)
      );
    });
  }, [documents, search]);

  const totalChunks = documents.reduce(
    (sum, doc) => sum + Number(doc.total_chunks || 0),
    0
  );

  const completedDocs = documents.filter(
    (doc) => String(doc.status || "").toUpperCase() === "COMPLETED"
  ).length;

  const vectorHealth = documents.length
    ? Math.round((completedDocs / documents.length) * 1000) / 10
    : 0;

  return (
    <div className="sd-kb-page">
      <div className="sd-kb-page-head">
        <div>
          <h1>KB Documents</h1>
          <p>Manage RAG source data for the SmartDesk AI engine.</p>
        </div>

        <div className="sd-kb-head-actions">
          <button
            className="sd-kb-outline-action"
            onClick={loadDocuments}
            disabled={uploading}
          >
            <Icon name="sync" />
            Re-index All
          </button>

          <button
            className="sd-kb-black-action"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            <Icon name="add" />
            Upload New Document
          </button>

          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".pdf,.txt,.docx,.md"
            onChange={handleFileChange}
          />
        </div>
      </div>

      <div className="sd-kb-layout">
        <aside className="sd-kb-left-column">
          <Card className="sd-kb-quick-upload-card">
            <h2>Quick Upload</h2>

            <button
              className="sd-kb-upload-drop"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(event) => event.preventDefault()}
              onDrop={handleDrop}
              disabled={uploading}
            >
              <Icon name="upload_file" />

              <strong>
                {uploading ? "Uploading document..." : "Drop files here or click to browse"}
              </strong>

              <span>Supports PDF, MD, and TXT (Max 50MB)</span>
            </button>
          </Card>

          <Card className="sd-kb-health-black-card">
            <div>
              <p>VECTOR DB HEALTH</p>
              <h2>{vectorHealth || 0}%</h2>
              <span>{totalChunks} segments indexed</span>
            </div>

            <div className="sd-kb-db-watermark">
              <Icon name="database" />
            </div>

            <div className="sd-kb-health-line">
              <div style={{ width: `${vectorHealth || 8}%` }} />
            </div>
          </Card>

          <Card className="sd-kb-pipeline-card">
            <h3>INGESTION PIPELINE</h3>

            <div className="sd-kb-pipeline-row">
              <span>Worker Node 01</span>
              <strong className="active">Active</strong>
            </div>

            <div className="sd-kb-pipeline-row">
              <span>Model Latency</span>
              <strong>142ms</strong>
            </div>

            <div className="sd-kb-pipeline-row">
              <span>Embedding Model</span>
              <strong>all-MiniLM-L6-v2</strong>
            </div>
          </Card>
        </aside>

        <section className="sd-kb-repository-card">
          <div className="sd-kb-repository-head">
            <h2>Repository Items</h2>

            <div className="sd-kb-search-box">
              <Icon name="search" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Filter documents..."
              />
            </div>
          </div>

          <div className="sd-kb-table-wrap">
            <table className="sd-kb-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Size</th>
                  <th>Uploaded</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <div className="sd-kb-file-cell">
                        <Icon name="description" />

                        <div>
                          <strong>{getDocumentName(doc)}</strong>
                          <span>{getDocumentType(doc)}</span>

                          {doc.error_message && (
                            <small className="sd-kb-error-text">
                              {doc.error_message}
                            </small>
                          )}
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="sd-kb-size">
                        {doc.file_size || doc.size || "--"}
                      </span>
                      <small>{doc.total_chunks || 0} chunks</small>
                    </td>

                    <td>
                      <span>{formatDateTime(doc.created_at)}</span>
                    </td>

                    <td>
                      <span
                        className={`sd-kb-status ${getStatusClass(doc.status)}`}
                      >
                        <span />
                        {getStatusText(doc.status)}
                      </span>
                    </td>

                    <td>
                      <button
                        className="sd-kb-delete-mini"
                        onClick={() => handleDelete(doc.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredDocuments.length === 0 && (
              <div className="sd-kb-empty-state">
                No KB documents found.
              </div>
            )}
          </div>

          <div className="sd-kb-repository-footer">
            <span>
              Showing {filteredDocuments.length} of {documents.length} documents
            </span>

            <div>
              <button disabled>
                <Icon name="chevron_left" />
              </button>
              <button>
                <Icon name="chevron_right" />
              </button>
            </div>
          </div>
        </section>
      </div>

      <Card className="sd-kb-semantic-card">
        <div className="sd-kb-semantic-head">
          <div>
            <h2>Semantic Mapping Cluster</h2>
            <p>
              Visualization of document relationships based on vector embeddings.
            </p>
          </div>

          <Icon name="fullscreen" />
        </div>

        <div className="sd-kb-cluster-area">
          <div className="sd-kb-cluster-visual">
            <span className="node n1" />
            <span className="node n2" />
            <span className="node n3" />
            <span className="node n4" />
            <span className="node n5" />
            <span className="node n6" />
            <span className="node n7" />

            <span className="line l1" />
            <span className="line l2" />
            <span className="line l3" />
            <span className="line l4" />
          </div>

          <div className="sd-kb-cluster-label">
            Real-time document cluster map (Conceptual)
          </div>
        </div>
      </Card>
    </div>
  );
}