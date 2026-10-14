import Foundation

/// Coasting after the fingers lift: velocity decays exponentially until it drops
/// below `stopVelocity`.
public struct ScrollMomentum: Sendable {
    public private(set) var velocityX: Double
    public private(set) var velocityY: Double
    private let tuning: TrackpadTuning.Momentum

    /// Nil when momentum is off or the flick was too slow to coast. `fingerTravel`
    /// (points moved during the gesture) weakens the coast of short swipes.
    public init?(velocityX: Double, velocityY: Double, fingerTravel: Double, tuning: TrackpadTuning.Momentum) {
        let rawSpeed = hypot(velocityX, velocityY)
        guard tuning.enabled, rawSpeed.isFinite, fingerTravel.isFinite else { return nil }
        let travelScale = tuning.fullCoastTravel > 0 ? min(1, max(0, fingerTravel) / tuning.fullCoastTravel) : 1
        let speed = rawSpeed * travelScale
        guard speed >= tuning.minStartVelocity else { return nil }
        let scale = travelScale * min(1, tuning.maxVelocity / speed)
        self.velocityX = velocityX * scale
        self.velocityY = velocityY * scale
        self.tuning = tuning
    }

    public var isFinished: Bool {
        hypot(velocityX, velocityY) < tuning.stopVelocity
    }

    /// Distance travelled over `dt` seconds, integrated exactly so frame rate
    /// doesn't change how far a flick goes.
    public mutating func step(dt: Double) -> (dx: Double, dy: Double) {
        guard dt > 0, !isFinished else { return (0, 0) }
        let kept = tuning.velocityKeptPerSecond
        let decay = pow(kept, dt)
        let travel = (decay - 1) / log(kept)
        let delta = (velocityX * travel, velocityY * travel)
        velocityX *= decay
        velocityY *= decay
        return delta
    }
}
