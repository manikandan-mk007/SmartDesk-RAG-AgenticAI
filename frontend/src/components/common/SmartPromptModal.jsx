import { useState } from "react";
import Button from "./Button";

export default function SmartPromptModal({
  open,
  title,
  label,
  placeholder,
  confirmText = "Submit",
  cancelText = "Cancel",
  onConfirm,
  onCancel,
}) {
  const [value, setValue] = useState("");

  if (!open) return null;

  const handleSubmit = (e) => {
    e.preventDefault();

    onConfirm(value);
    setValue("");
  };

  const handleCancel = () => {
    setValue("");
    onCancel();
  };

  return (
    <div className="sd-modal-backdrop">
      <div className="sd-smart-prompt-modal">
        <h2 className="sd-heading-sm">{title}</h2>

        <form onSubmit={handleSubmit} className="sd-mt-4">
          <label className="sd-form-label">{label}</label>

          <textarea
            className="sd-textarea"
            rows="4"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={placeholder}
            autoFocus
          />

          <div className="sd-row sd-mt-5" style={{ justifyContent: "flex-end" }}>
            <Button variant="secondary" onClick={handleCancel}>
              {cancelText}
            </Button>

            <Button type="submit">
              {confirmText}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}