import XCTest

@testable import RemoteClientCore

final class TrackpadTuningTests: XCTestCase {
    private let momentum = TrackpadTuning.Momentum(
        enabled: true, velocityKeptPerSecond: 0.135,
        minStartVelocity: 100, stopVelocity: 10, maxVelocity: 5000, fullCoastTravel: 200
    )

    /// Catches a broken edit to the JSON before it reaches the phone.
    func testBundledFileDecodesWithSaneValues() {
        let tuning = TrackpadTuning.bundled
        for gain in [tuning.cursor, tuning.scroll.gain] {
            XCTAssertGreaterThan(gain.speed, 0)
            XCTAssertGreaterThanOrEqual(gain.accelerationPer1000, 0)
            XCTAssertGreaterThanOrEqual(gain.maxSpeed, gain.speed)
        }
        let momentum = tuning.scroll.momentum
        XCTAssertGreaterThan(momentum.velocityKeptPerSecond, 0)
        XCTAssertLessThan(momentum.velocityKeptPerSecond, 1)
        XCTAssertGreaterThan(momentum.stopVelocity, 0)
        XCTAssertGreaterThanOrEqual(momentum.minStartVelocity, momentum.stopVelocity)
        XCTAssertGreaterThanOrEqual(momentum.maxVelocity, momentum.minStartVelocity)
        XCTAssertGreaterThan(momentum.fullCoastTravel, 0)
        XCTAssertGreaterThan(tuning.gestures.swipeDistance, 0)
        XCTAssertGreaterThan(tuning.gestures.dragHoldSeconds, 0)
    }

    func testGainRampsWithFingerSpeedUpToTheCap() {
        let gain = TrackpadTuning.Gain(speed: 1, accelerationPer1000: 2, maxSpeed: 4)
        XCTAssertEqual(gain.gain(forFingerSpeed: 0), 1)
        XCTAssertEqual(gain.gain(forFingerSpeed: 500), 2)
        XCTAssertEqual(gain.gain(forFingerSpeed: 10_000), 4)
    }

    func testMomentumDoesNotStartWhenSlowOrDisabled() {
        XCTAssertNil(ScrollMomentum(velocityX: 60, velocityY: 60, fingerTravel: 200, tuning: momentum))
        var off = momentum
        off.enabled = false
        XCTAssertNil(ScrollMomentum(velocityX: 0, velocityY: 3000, fingerTravel: 200, tuning: off))
    }

    func testMomentumIsCappedAndKeepsDirection() throws {
        let coast = try XCTUnwrap(ScrollMomentum(velocityX: -30_000, velocityY: 40_000, fingerTravel: 200, tuning: momentum))
        XCTAssertEqual(coast.velocityX, -3000, accuracy: 0.001)
        XCTAssertEqual(coast.velocityY, 4000, accuracy: 0.001)
    }

    private func coastVelocityY(_ v: Double, travel: Double, _ tuning: TrackpadTuning.Momentum? = nil) -> Double? {
        ScrollMomentum(velocityX: 0, velocityY: v, fingerTravel: travel, tuning: tuning ?? momentum)?.velocityY
    }

    func testShortTravelCoastsProportionallyWeakerThanLongTravel() throws {
        let long = try XCTUnwrap(coastVelocityY(2000, travel: 200))
        let short = try XCTUnwrap(coastVelocityY(2000, travel: 50))
        XCTAssertEqual(long, 2000, accuracy: 0.001)
        XCTAssertEqual(short, 500, accuracy: 0.001)
    }

    func testTravelAtOrBeyondFullCoastTravelIsUnscaled() {
        XCTAssertEqual(coastVelocityY(2000, travel: 200) ?? 0, 2000, accuracy: 0.001)
        XCTAssertEqual(coastVelocityY(2000, travel: 5000) ?? 0, 2000, accuracy: 0.001)
    }

    func testShortSlowFlickDoesNotCoast() {
        // 300 px/s alone clears minStartVelocity (100), but 300 * 50/200 = 75 does not.
        XCTAssertNotNil(coastVelocityY(300, travel: 200))
        XCTAssertNil(coastVelocityY(300, travel: 50))
    }

    func testScaledVelocityNeverExceedsMaxVelocity() throws {
        for travel in [100.0, 200, 10_000] {
            let coast = try XCTUnwrap(ScrollMomentum(velocityX: 30_000, velocityY: -40_000, fingerTravel: travel, tuning: momentum))
            XCTAssertLessThanOrEqual(hypot(coast.velocityX, coast.velocityY), 5000 + 0.001)
        }
    }

    func testScaledCoastKeepsDirection() throws {
        let coast = try XCTUnwrap(ScrollMomentum(velocityX: -3000, velocityY: 4000, fingerTravel: 100, tuning: momentum))
        XCTAssertEqual(coast.velocityX, -1500, accuracy: 0.001)
        XCTAssertEqual(coast.velocityY, 2000, accuracy: 0.001)
    }

    func testNonPositiveFullCoastTravelAppliesNoScaling() {
        for full in [0.0, -50] {
            var t = momentum
            t.fullCoastTravel = full
            XCTAssertEqual(coastVelocityY(2000, travel: 1, t) ?? 0, 2000, accuracy: 0.001)
            XCTAssertEqual(coastVelocityY(2000, travel: 0, t) ?? 0, 2000, accuracy: 0.001)
        }
    }

    func testNonFiniteOrNegativeTravelDoesNotCoast() {
        for travel in [Double.nan, .infinity, -.infinity, -500, -0.0] {
            XCTAssertNil(coastVelocityY(5000, travel: travel), "travel \(travel)")
        }
    }

    func testMomentumDeceleratesToAStopIndependentOfFrameRate() throws {
        func coast(frame: Double) throws -> (distance: Double, frames: Int) {
            var momentum = try XCTUnwrap(ScrollMomentum(velocityX: 0, velocityY: 2000, fingerTravel: 200, tuning: self.momentum))
            var distance = 0.0
            var frames = 0
            var last = Double.infinity
            while !momentum.isFinished {
                let step = momentum.step(dt: frame).dy
                XCTAssertGreaterThan(step, 0)
                XCTAssertLessThan(step, last)
                last = step
                distance += step
                frames += 1
                if frames > 10_000 { XCTFail("never stopped"); break }
            }
            XCTAssertEqual(momentum.step(dt: frame).dy, 0)
            return (distance, frames)
        }
        let at60 = try coast(frame: 1.0 / 60)
        let at120 = try coast(frame: 1.0 / 120)
        XCTAssertEqual(at60.distance, at120.distance, accuracy: 2000 * 0.01)
        XCTAssertGreaterThan(at120.frames, at60.frames)
    }
}
