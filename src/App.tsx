/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export default function App() {
  return (
    <div className="flex flex-col h-screen w-full bg-[#0A0B0D] text-slate-300 font-sans overflow-hidden select-none">
      {/* Header / Navigation */}
      <nav className="flex items-center justify-between px-6 py-3 bg-[#111318] border-b border-slate-800">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white text-xs">CVCP</div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight text-slate-100">Engineering Execution Blueprint</h1>
            <p className="text-[10px] text-slate-500 font-mono">v1.1.0-Core • Codessa Reference Platform</p>
          </div>
        </div>
        <div className="flex items-center gap-6 text-[11px] font-medium">
          <span className="text-blue-400 border-b border-blue-400 py-1 cursor-pointer">PROTOCOL SPECS</span>
          <span className="text-slate-400 hover:text-slate-200 cursor-pointer transition-colors">SCHEMAS</span>
          <span className="text-slate-400 hover:text-slate-200 cursor-pointer transition-colors">TEST VECTORS</span>
          <span className="text-slate-400 hover:text-slate-200 text-opacity-50 cursor-pointer transition-colors">TCK_HARNESS</span>
          <div className="ml-4 px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full font-mono text-[9px]">STATUS: FROZEN</div>
        </div>
      </nav>

      {/* Main Content Layout */}
      <main className="flex-1 flex overflow-hidden">
        
        {/* Sidebar / Navigation Tree */}
        <aside className="w-64 border-r border-slate-800 bg-[#0E1015] p-4 flex flex-col gap-4">
          <section>
            <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Ingestion Manifest</h3>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-xs text-slate-300 bg-slate-800/50 p-2 rounded border border-slate-700 cursor-pointer">
                <span className="w-1 h-1 bg-blue-400 rounded-full"></span>
                cvcp-protocols/schemas
              </li>
              <li className="flex items-center gap-2 text-xs text-slate-500 p-2 hover:bg-slate-800/30 rounded cursor-pointer transition-colors">
                <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                cvcp-protocols/test-vectors
              </li>
              <li className="flex items-center gap-2 text-xs text-slate-500 p-2 hover:bg-slate-800/30 rounded cursor-pointer transition-colors">
                <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                cvcp-protocols/src/core
              </li>
            </ul>
          </section>

          <section className="mt-4">
            <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">M1 Components</h3>
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-[11px] text-slate-400">
                <span>Event Parser</span>
                <span className="text-blue-500 font-mono">COMPLIANT</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full">
                <div className="bg-blue-600 w-full h-full rounded-full"></div>
              </div>
              <div className="flex justify-between items-center text-[11px] text-slate-400 mt-2">
                <span>JCS Processor</span>
                <span className="text-blue-500 font-mono">READY</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full">
                <div className="bg-blue-600 w-full h-full rounded-full"></div>
              </div>
            </div>
          </section>
        </aside>

        {/* Working Area */}
        <section className="flex-1 flex flex-col bg-[#0A0B0D]">
          {/* Pipeline Visualizer */}
          <div className="p-6 border-b border-slate-800">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-6">5-Stage Parser Verification Routine</h2>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-24 bg-blue-500/5 border border-blue-500/20 rounded flex flex-col items-center justify-center gap-2 p-3 text-center">
                <span className="text-[9px] text-blue-400 font-mono">PHASE 1</span>
                <span className="text-[11px] font-bold text-slate-200 leading-tight">WIRE PARSE</span>
              </div>
              <div className="text-slate-600">→</div>
              <div className="flex-1 h-24 bg-slate-800/30 border border-slate-700 rounded flex flex-col items-center justify-center gap-2 p-3 text-center">
                <span className="text-[9px] text-slate-500 font-mono">PHASE 2</span>
                <span className="text-[11px] font-bold text-slate-200 leading-tight">SCHEMA MATCH</span>
              </div>
              <div className="text-slate-600">→</div>
              <div className="flex-1 h-24 bg-slate-800/30 border border-slate-700 rounded flex flex-col items-center justify-center gap-2 p-3 text-center">
                <span className="text-[9px] text-slate-500 font-mono">PHASE 3</span>
                <span className="text-[11px] font-bold text-slate-200 leading-tight">CANONICALIZE</span>
              </div>
              <div className="text-slate-600">→</div>
              <div className="flex-1 h-24 bg-slate-800/30 border border-slate-700 rounded flex flex-col items-center justify-center gap-2 p-3 text-center">
                <span className="text-[9px] text-slate-500 font-mono">PHASE 4</span>
                <span className="text-[11px] font-bold text-slate-200 leading-tight">CRYPTO CHECK</span>
              </div>
              <div className="text-slate-600">→</div>
              <div className="flex-1 h-24 bg-green-500/10 border border-green-500/30 rounded flex flex-col items-center justify-center gap-2 p-3 text-center">
                <span className="text-[9px] text-green-400 font-mono">PHASE 5</span>
                <span className="text-[11px] font-bold text-slate-200 leading-tight">COMMIT LEDGER</span>
              </div>
            </div>
          </div>

          {/* Split Detail View */}
          <div className="flex-1 flex min-h-0">
            {/* Error Registry */}
            <div className="flex-1 p-6 overflow-hidden flex flex-col">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Protocol Error Registry</h3>
              <div className="flex-1 border border-slate-800 rounded-lg overflow-hidden bg-[#0E1015]">
                <table className="w-full text-left text-[11px]">
                  <thead className="bg-slate-800/50 text-slate-400 uppercase font-bold">
                    <tr>
                      <th className="p-3">Protocol Error Code</th>
                      <th className="p-3">Invariant Trigger</th>
                      <th className="p-3">Remediation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-400">
                    <tr>
                      <td className="p-3 font-mono text-red-400">ERR_EVENT_SYNTAX</td>
                      <td className="p-3">Malformed JSON ingress</td>
                      <td className="p-3">Terminate Session</td>
                    </tr>
                    <tr className="bg-slate-900/50">
                      <td className="p-3 font-mono text-amber-400">ERR_EVENT_SCHEMA</td>
                      <td className="p-3">Missing correlation_id</td>
                      <td className="p-3">Isolate Log</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-orange-500">ERR_EVENT_CHECKSUM</td>
                      <td className="p-3">SHA-256 Mismatch</td>
                      <td className="p-3 text-red-500 font-bold uppercase">Critical State Freeze</td>
                    </tr>
                    <tr className="bg-slate-900/50">
                      <td className="p-3 font-mono text-blue-400">ERR_EVENT_SEMANTICS</td>
                      <td className="p-3">Causal order violation</td>
                      <td className="p-3">Rollback Graph</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Schema/Code Block */}
            <div className="w-80 border-l border-slate-800 bg-[#0E1015] p-6 flex flex-col">
               <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Core Constraints</h3>
               <div className="flex-1 bg-black/40 rounded p-4 font-mono text-[10px] text-blue-200/80 leading-relaxed overflow-hidden">
                 <span className="text-slate-500">{'// RFC-0001 Integrity Block'}</span><br/>
                 {'{'}<br/>
                   <span className="text-blue-400 ml-4">"algorithm"</span>: "SHA-256",<br/>
                   <span className="text-blue-400 ml-4">"canonicalization"</span>: "RFC8785",<br/>
                   <span className="text-blue-400 ml-4">"checksum"</span>: "1349f50f...3da65"<br/>
                 {'}'}<br/><br/>
                 <span className="text-slate-500">{'// Invariants'}</span><br/>
                 - <span className="text-slate-300">Identity</span>: UUIDv7 Only<br/>
                 - <span className="text-slate-300">Temporal</span>: ISO 8601 (Z)<br/>
                 - <span className="text-slate-300">Lexical</span>: Sorted Keys (JCS)
               </div>
               <button className="mt-4 w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-4 rounded text-xs tracking-widest uppercase cursor-pointer transition-colors">
                 Initialize Phase 1
               </button>
            </div>
          </div>
        </section>
      </main>

      {/* Bottom Status Bar */}
      <footer className="bg-[#111318] border-t border-slate-800 px-6 py-2 flex items-center justify-between text-[10px] font-mono">
        <div className="flex items-center gap-4">
          <span className="text-slate-500">MILESTONE TRACK:</span>
          <div className="flex gap-1 items-center">
             <div className="w-3 h-3 bg-blue-600 rounded-full border border-blue-400"></div>
             <div className="w-12 h-1 bg-blue-600"></div>
             <div className="w-3 h-3 bg-slate-700 rounded-full"></div>
             <div className="w-12 h-1 bg-slate-800"></div>
             <div className="w-3 h-3 bg-slate-700 rounded-full"></div>
             <div className="w-12 h-1 bg-slate-800"></div>
             <span className="ml-2 text-slate-400">M3: REFERENCE RUNTIME (PENDING)</span>
          </div>
        </div>
        <div className="text-slate-600">
          SYSTEM CLOCK: 2026-07-02T14:32:00.000Z
        </div>
      </footer>
    </div>
  );
}
