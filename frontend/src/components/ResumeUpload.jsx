import { useRef, useState } from "react";

export default function ResumeUpload({ file, onFileSelected }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleFiles(fileList) {
    if (fileList && fileList[0]) {
      onFileSelected(fileList[0]);
    }
  }

  return (
    <div>
      <label className="block font-serif text-lg mb-2">1. Your resume</label>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer border rounded-sm px-5 py-6 text-sm transition-colors
          ${isDragging ? "border-teal bg-teal-soft/40" : "border-line hover:border-ink-soft"}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        {file ? (
          <p className="text-ink">
            <span className="font-medium">{file.name}</span>
            <span className="text-ink-soft"> — click to replace</span>
          </p>
        ) : (
          <p className="text-ink-soft">
            Drop a PDF or DOCX resume here, or click to browse.
          </p>
        )}
      </div>
    </div>
  );
}
