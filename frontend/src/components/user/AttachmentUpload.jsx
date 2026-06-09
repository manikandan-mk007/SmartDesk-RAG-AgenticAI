import { useState } from "react";
import { uploadTicketAttachment } from "../../api/ticketApi";
import Button from "../common/Button";
import Icon from "../common/Icon";

export default function AttachmentUpload({ ticket, onRefresh }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      await uploadTicketAttachment(ticket.id, file);
      setFile(null);
      onRefresh();
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="sd-card pad">
      <div className="sd-section-title-row">
        <Icon name="attach_file" />
        <h3 className="sd-heading-sm">Attachments</h3>
      </div>

      {ticket.status !== "CLOSED" && (
        <div className="sd-row sd-mb-4">
          <input className="sd-input" type="file" onChange={(e) => setFile(e.target.files[0])} />
          <Button onClick={handleUpload} disabled={!file || uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </Button>
        </div>
      )}

      {ticket.attachments?.length === 0 && (
        <p className="sd-body sd-muted">No attachments uploaded.</p>
      )}

      {ticket.attachments?.map((item) => (
        <div key={item.id} className="sd-attachment-item">
          <div className="sd-row-between">
            <div>
              <p className="sd-ticket-title">{item.original_filename}</p>
              <p className="sd-label-sm sd-muted">{item.file_type}</p>
            </div>

            {item.file_url && (
              <a className="sd-nav-link active" href={item.file_url} target="_blank" rel="noreferrer">
                View
              </a>
            )}
          </div>

          {item.analysis_result && (
            <pre className="sd-pre sd-mt-3">{item.analysis_result}</pre>
          )}
        </div>
      ))}
    </div>
  );
}