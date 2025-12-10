"""
RouteCam v2 Director
====================
Manages the temporal aspect of the animation.
Maps Frame Numbers -> Normalized Story Time (Sigma).
Implements "Elastic Pacing".
"""

class Director:
    def __init__(self, duration_frames=120, beats=None):
        self.duration = duration_frames
        
        # Beat definitions (Normalized 0.0 - 1.0)
        if beats:
            self.beats = beats
        else:
            self.beats = {
                'establish': 0.0,
                'drift_start': 0.2,
                'zoom_start': 0.4,
                'chase': 1.0
            }
        
    def get_sigma(self, frame, frame_start):
        """
        Maps a specific frame number to the normalized ACTION time (sigma).
        Input: Frame (e.g., 60), Start (e.g., 1)
        Output: Sigma (0.0 to 1.0) - warped by beats
        """
        if self.duration <= 0: return 0.0
        
        rel_frame = frame - frame_start
        t = max(0.0, min(1.0, rel_frame / self.duration))
        
        # Beats
        t_drift = self.beats.get('drift_start', 0.2)
        t_zoom = self.beats.get('zoom_start', 0.4)
        
        # Targets for Sigma (Action Amount)
        # At drift_start, we are at 0.0 action (End of pure static establish)
        # At zoom_start, we are at say 0.1 action (End of slow drift)
        # At 1.0, we are at 1.0 action (End of chase)
        
        SIGMA_AT_ZOOM = 0.15 # How much we have moved by the time Zoom starts
        
        if t <= t_drift:
            # Phase 1: Establish (Static or Micro-movement)
            # Let's keep it 0.0 for pure establish
            return 0.0
            
        elif t <= t_zoom:
            # Phase 2: Drift (Slow move)
            # Map range [t_drift, t_zoom] -> [0.0, SIGMA_AT_ZOOM]
            domain = t_zoom - t_drift
            if domain < 1e-5: return SIGMA_AT_ZOOM
            ratio = (t - t_drift) / domain
            # Smooth ease in
            ratio = ratio * ratio * (3 - 2 * ratio)
            return ratio * SIGMA_AT_ZOOM
            
        else:
            # Phase 3: Zoom (Fast move)
            # Map range [t_zoom, 1.0] -> [SIGMA_AT_ZOOM, 1.0]
            domain = 1.0 - t_zoom
            if domain < 1e-5: return 1.0
            ratio = (t - t_zoom) / domain
            # Ease in-out
            # ratio = ratio * ratio * (3 - 2 * ratio) 
            # Actually for zoom we might want acceleration? Let's stick to cubic for smoothness.
            ease = ratio * ratio * (3 - 2 * ratio)
            return SIGMA_AT_ZOOM + ease * (1.0 - SIGMA_AT_ZOOM)
        
    def get_beat_value(self, beat_name):
        """Returns the normalized time for a named beat."""
        return self.beats.get(beat_name, 0.0)
        
    def get_segment_easing(self, t):
        """
        Returns a specific easing curve value for the current time t.
        We can apply different easings for different phases (Drift vs Zoom).
        """
        # For now, simple cubic ease-in-out for everything
        # t^2(3-2t)
        return t * t * (3 - 2 * t)
