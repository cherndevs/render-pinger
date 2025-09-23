export default async function handler(req, res) {
  // Only allow cron jobs to trigger this (security)
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const targetUrl = process.env.RENDER_URL;
  
  if (!targetUrl) {
    return res.status(500).json({ error: 'RENDER_URL not configured' });
  }

  try {
    const startTime = Date.now();
    
    const response = await fetch(`${targetUrl}/health`, {
      method: 'GET',
      headers: {
        'User-Agent': 'Vercel-Keepalive-Bot/1.0'
      },
      // 8 second timeout (Vercel functions have 10s limit on free tier)
      signal: AbortSignal.timeout(8000)
    });
    
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    if (response.ok) {
      console.log(`✅ Ping successful: ${response.status} (${responseTime}ms)`);
      return res.status(200).json({
        success: true,
        status: response.status,
        responseTime: `${responseTime}ms`,
        timestamp: new Date().toISOString(),
        target: targetUrl
      });
    } else {
      console.log(`❌ Ping failed: ${response.status}`);
      return res.status(200).json({
        success: false,
        status: response.status,
        responseTime: `${responseTime}ms`,
        timestamp: new Date().toISOString()
      });
    }
    
  } catch (error) {
    console.error('Ping error:', error.message);
    return res.status(200).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
