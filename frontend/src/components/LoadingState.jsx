export default function LoadingState({ label = "Loading analysis" }) {
  return (
    <div className="state-panel" role="status">
      <div className="spinner" aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}
