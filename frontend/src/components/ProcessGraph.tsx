import type { ProcessGraph } from "../types/contracts";

export function ProcessGraphView({ graph }: { graph: ProcessGraph }) {
  const getNode = (id: string) => graph.nodes.find((node) => node.id === id);

  return (
    <div className="panel-strong data-grid overflow-hidden rounded-[2rem] p-6">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="eyebrow">Process graph</p>
          <h3 className="display-text mt-2 text-2xl">Observed path</h3>
        </div>
        <p className="max-w-sm text-right text-sm leading-6 text-[color:var(--muted)]">
          Weighted edges show the strongest path, while the loop highlights where
          clarification reopens earlier work.
        </p>
      </div>

      <svg viewBox="0 0 100 48" className="w-full">
        {graph.edges.map((edge) => {
          const source = getNode(edge.source);
          const target = getNode(edge.target);

          if (!source || !target) {
            return null;
          }

          const midX = (source.x + target.x) / 2;
          const midY = (source.y + target.y) / 2;
          const curve = source.y === target.y ? 0 : source.y < target.y ? 6 : -6;
          const path = `M ${source.x} ${source.y} C ${midX} ${source.y + curve}, ${
            midX
          } ${target.y - curve}, ${target.x} ${target.y}`;

          return (
            <g key={`${edge.source}-${edge.target}`}>
              <path
                d={path}
                fill="none"
                stroke="rgba(15, 118, 110, 0.42)"
                strokeLinecap="round"
                strokeWidth={Math.max(1.5, edge.weight / 28)}
                strokeDasharray={edge.label ? "4 3" : undefined}
              />
              {edge.label ? (
                <text
                  x={midX}
                  y={midY - 2}
                  textAnchor="middle"
                  fontSize="2.6"
                  fill="rgba(24, 23, 19, 0.65)"
                >
                  {edge.label}
                </text>
              ) : null}
            </g>
          );
        })}

        {graph.nodes.map((node) => {
          const fill =
            node.tier === "decision"
              ? "rgba(162, 75, 42, 0.18)"
              : node.tier === "start" || node.tier === "end"
                ? "rgba(15, 118, 110, 0.18)"
                : "rgba(255, 255, 255, 0.95)";

          return (
            <g key={node.id}>
              <circle
                cx={node.x}
                cy={node.y}
                r={Math.max(3.8, 3.6 + node.emphasis / 48)}
                fill={fill}
                stroke="rgba(24, 23, 19, 0.18)"
                strokeWidth="0.6"
              />
              <text
                x={node.x}
                y={node.y - 6.2}
                textAnchor="middle"
                fontSize="2.7"
                fill="rgba(24, 23, 19, 0.75)"
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
