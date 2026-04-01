import React, { useState, useRef } from 'react';

const FarmerPanel = ({ diseaseData }) => {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('hi');
  const [area, setArea] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const handleExplain = async () => {
    setLoading(true);
    setExplanation(null);
    try {
      const payload = { ...diseaseData, language, area };
      const response = await fetch('/full-explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      setExplanation(data);
    } catch (err) {
      console.error(err);
      alert("Uh oh! AI explanation failed. Check network.");
    } finally {
      setLoading(false);
    }
  };

  const playVoice = () => {
    if (explanation?.audio_url) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      const audio = new Audio(explanation.audio_url);
      audioRef.current = audio;
      
      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => { alert("Voice playback failed."); setIsPlaying(false); };
      
      audio.play();
    }
  };

  return (
    <div className="max-w-md mx-auto bg-green-50 shadow-2xl overflow-hidden md:max-w-xl my-6 rounded-3xl border border-green-200">
      
      {/* Top Banner Control Panel */}
      <div className="bg-white p-6 border-b border-green-100 flex flex-col gap-4">
        <h2 className="text-3xl font-black text-green-900 tracking-tight text-center">Farming Assistant</h2>
        
        <div className="flex gap-2">
          <select 
            value={language} 
            onChange={e => setLanguage(e.target.value)}
            className="flex-1 bg-green-100 text-green-900 font-bold p-3 rounded-xl outline-none"
          >
            <option value="hi">हिंदी (Hindi)</option>
            <option value="en">English</option>
            <option value="mr">मराठी (Marathi)</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="te">తెలుగు (Telugu)</option>
          </select>
          <input 
            type="number" 
            min="1" 
            value={area} 
            onChange={e => setArea(e.target.value)}
            className="w-24 bg-green-100 text-green-900 font-bold p-3 rounded-xl outline-none text-center"
            placeholder="Acres"
          />
        </div>
        
        <button 
          onClick={handleExplain} 
          disabled={loading || !diseaseData} 
          className="w-full bg-green-600 hover:bg-green-700 active:scale-95 text-white text-xl font-bold py-4 rounded-2xl shadow-lg transition-transform"
        >
          {loading ? '🤖 Analyzing Info...' : 'Get Simple Advice'}
        </button>
      </div>

      {/* Results View */}
      {explanation && (
        <div className="p-6 space-y-6">
          
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-black text-gray-800">{explanation.title}</h3>
            {explanation.audio_url && (
              <button 
                onClick={playVoice} 
                className={`flex items-center gap-2 px-4 py-2 rounded-full font-bold shadow-md transition-colors ${isPlaying ? 'bg-orange-500 text-white animate-pulse' : 'bg-green-200 text-green-900'}`}
              >
                🔊 {isPlaying ? 'Playing...' : 'Listen'}
              </button>
            )}
          </div>

          <p className="text-lg leading-relaxed text-gray-700 font-medium">
            {explanation.summary}
          </p>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-orange-100">
            <h4 className="text-xl font-bold text-orange-600 flex items-center mb-3">⚠️ What to do now</h4>
            <ul className="space-y-3">
              {explanation.actions.map((act, i) => (
                <li key={i} className="flex gap-3 text-gray-700 text-lg">
                  <span className="text-orange-500 font-bold">✓</span> {act}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-blue-100">
            <h4 className="text-xl font-bold text-blue-600 flex items-center mb-2">🛡️ Precautions</h4>
            <ul className="space-y-2 text-gray-600 text-lg">
              {explanation.precautions.map((prec, i) => (
                <li key={i} className="flex gap-2"><span className="text-blue-400">•</span> {prec}</li>
              ))}
            </ul>
          </div>

          <div className="bg-green-900 text-green-100 rounded-2xl p-5 shadow-lg relative overflow-hidden">
             <div className="absolute opacity-10 right-[-10px] top-[-10px] text-8xl">💰</div>
             <h4 className="text-xl font-bold text-white mb-2 relative z-10">Cost Estimate</h4>
             <div className="flex flex-col gap-1 relative z-10">
               <span className="text-green-300">Rate: <strong className="text-white text-lg">{explanation.cost}</strong></span>
               <span className="text-green-300">Total (for {area} acres): <strong className="text-yellow-400 text-xl">{explanation.total_cost}</strong></span>
             </div>
          </div>
          
        </div>
      )}
    </div>
  );
};
export default FarmerPanel;
