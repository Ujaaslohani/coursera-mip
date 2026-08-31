import React from "react";

export function Loader({ className }: { className?: string }) {
  return (
    <div className={`typewriter ${className || ""}`}>
      <div className="slide">
        <i></i>
      </div>
      <div className="paper"></div>
      <div className="keyboard"></div>
    </div>
  );
}

export default Loader;
