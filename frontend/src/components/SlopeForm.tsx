import { useState, type FormEvent } from "react";
import type { AnalyzeRequest, Method } from "../api/types";

interface Props {
  onSubmit: (req: AnalyzeRequest) => void;
  loading: boolean;
}

function NumberInput(props: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  step?: number | "any";
}) {
  return (
    <label className="flex flex-col text-sm">
      <span className="mb-1 text-slate-600">{props.label}</span>
      <input
        type="number"
        step={props.step ?? "any"}
        value={props.value}
        onChange={(e) => props.onChange(Number(e.target.value))}
        className="rounded border border-slate-300 px-2 py-1"
      />
    </label>
  );
}

export default function SlopeForm({ onSubmit, loading }: Props) {
  const [method, setMethod] = useState<Method>("bishop");
  const [height, setHeight] = useState(10);
  const [angle, setAngle] = useState(26.565);
  const [centerX, setCenterX] = useState(4.206);
  const [centerY, setCenterY] = useState(22.4018);
  const [radius, setRadius] = useState(22.7932);
  const [cohesion, setCohesion] = useState(10);
  const [phi, setPhi] = useState(20);
  const [gamma, setGamma] = useState(20);
  const [ru, setRu] = useState(0.25);
  const [numSlices, setNumSlices] = useState(50);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({
      method,
      geometry: { height, angle },
      slip_circle: { center_x: centerX, center_y: centerY, radius },
      soil: { cohesion, phi, gamma, ru },
      num_slices: numSlices,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <label className="flex flex-col text-sm">
        <span className="mb-1 text-slate-600">Método</span>
        <select
          value={method}
          onChange={(e) => setMethod(e.target.value as Method)}
          className="rounded border border-slate-300 px-2 py-1"
        >
          <option value="bishop">Bishop simplificado</option>
          <option value="fellenius">Fellenius (ordinario)</option>
        </select>
      </label>

      <div>
        <p className="mb-2 text-sm font-semibold text-slate-700">Talud</p>
        <div className="grid grid-cols-2 gap-3">
          <NumberInput label="Altura (m)" value={height} onChange={setHeight} />
          <NumberInput label="Ángulo (°)" value={angle} onChange={setAngle} />
        </div>
      </div>

      <div>
        <p className="mb-2 text-sm font-semibold text-slate-700">Círculo</p>
        <div className="grid grid-cols-3 gap-3">
          <NumberInput label="Centro X (m)" value={centerX} onChange={setCenterX} />
          <NumberInput label="Centro Y (m)" value={centerY} onChange={setCenterY} />
          <NumberInput label="Radio (m)" value={radius} onChange={setRadius} />
        </div>
      </div>

      <div>
        <p className="mb-2 text-sm font-semibold text-slate-700">Suelo</p>
        <div className="grid grid-cols-2 gap-3">
          <NumberInput
            label="Cohesión (kPa)"
            value={cohesion}
            onChange={setCohesion}
          />
          <NumberInput label="Phi (°)" value={phi} onChange={setPhi} />
          <NumberInput label="Gamma (kN/m³)" value={gamma} onChange={setGamma} />
          <NumberInput label="ru" value={ru} onChange={setRu} />
        </div>
      </div>

      <NumberInput
        label="N° de dovelas"
        value={numSlices}
        onChange={setNumSlices}
        step={1}
      />

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-slate-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
      >
        {loading ? "Calculando..." : "Calcular"}
      </button>
    </form>
  );
}
