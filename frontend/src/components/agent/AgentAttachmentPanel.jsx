import Icon from "../common/Icon";

function getMediaUrl(fileUrl) {
  if (!fileUrl) return "";

  if (fileUrl.startsWith("http://") || fileUrl.startsWith("https://")) {
    return fileUrl;
  }

  if (fileUrl.startsWith("/media/")) {
    return `http://127.0.0.1:8000${fileUrl}`;
  }

  return fileUrl;
}

export default function AgentAttachmentPanel({ attachments = [] }) {
  return (
    <div className="sd-card pad">
      <div className="sd-section-title-row">
        <div className="sd-icon-box">
          <Icon name="attach_file" />
        </div>
        <div>
          <h2 className="sd-heading-sm">User Attachments</h2>
          <p className="sd-body sd-muted">
            Uploaded screenshots, videos, and automatic analysis results.
          </p>
        </div>
      </div>

      {attachments.length === 0 ? (
        <p className="sd-body sd-muted sd-mt-4">
          No image or video attachments uploaded by the user.
        </p>
      ) : (
        <div className="sd-agent-attachment-grid sd-mt-5">
          {attachments.map((item) => {
            const fileUrl = getMediaUrl(item.file_url || item.file);
            const fileType = String(item.file_type || "").toUpperCase();

            return (
              <div key={item.id} className="sd-agent-attachment-card">
                <div className="sd-row-between">
                  <div>
                    <p className="sd-ticket-title">
                      {item.original_filename || "Attachment"}
                    </p>
                    <p className="sd-label-sm sd-muted">{fileType}</p>
                  </div>

                  {fileUrl && (
                    <a
                      className="sd-btn sd-btn-secondary"
                      href={fileUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      View
                    </a>
                  )}
                </div>

                {fileType === "IMAGE" && fileUrl && (
                  <img
                    src={fileUrl}
                    alt={item.original_filename || "Ticket attachment"}
                    className="sd-agent-attachment-image"
                  />
                )}

                {fileType === "VIDEO" && fileUrl && (
                  <video
                    src={fileUrl}
                    controls
                    className="sd-agent-attachment-video"
                  />
                )}

                {item.analysis_result && (
                  <div className="sd-agent-analysis-box">
                    <p className="sd-label sd-muted">AI Attachment Analysis</p>
                    <pre className="sd-pre sd-mt-2">{item.analysis_result}</pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}