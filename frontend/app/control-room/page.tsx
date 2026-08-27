import { fetchControlRoom } from "../../lib/api";
import { ControlRoomClient } from "./ControlRoomClient";

export default async function ControlRoomPage() {
  let data = null;
  let error = null;
  try {
    data = await fetchControlRoom();
  } catch (e) {
    error = (e as Error).message;
  }

  if (error || !data) {
    return (
      <main className="mx-auto max-w-6xl px-6 py-12 text-center text-slate-600">
        <p>Control Room unavailable. Start backend: uvicorn app.main:app --reload</p>
        <p className="mt-2 text-sm text-red-600">{error}</p>
      </main>
    );
  }

  return <ControlRoomClient data={data} />;
}
