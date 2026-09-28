export default function JobDescriptionInput({ value, onChange }) {
  return (
    <div>
      <label className="block font-serif text-lg mb-2">2. Job description</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste the full job posting here — the more detail, the better the analysis."
        rows={8}
        className="w-full border border-line rounded-sm px-4 py-3 text-sm text-ink
          placeholder:text-ink-soft focus:outline-none focus:border-teal resize-y"
      />
    </div>
  );
}
