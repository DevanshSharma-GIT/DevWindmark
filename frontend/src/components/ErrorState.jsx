export default function ErrorState({ message }) {
  return (
    <div className="state-panel error" role="alert">
      <p>The analysis could not be loaded.</p>
      <p>{message}</p>
    </div>
  );
}
