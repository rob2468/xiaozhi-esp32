#pragma once

// Main-task-only policy. Network callbacks must schedule mutations on the main task.
class KeywordTurn {
public:
    void Wake() { phase_ = Phase::Listening; }
    void Reset() { phase_ = Phase::Idle; }
    bool IsListening() const { return phase_ == Phase::Listening; }
    bool AcceptTranscript() {
        if (!IsListening())
            return false;
        phase_ = Phase::Waiting;
        return true;
    }
    bool StartReply() {
        if (phase_ != Phase::Waiting)
            return false;
        phase_ = Phase::Speaking;
        return true;
    }
    void StopReply() {
        if (phase_ == Phase::Speaking)
            phase_ = Phase::Draining;
    }
    bool FinishPlayback(bool drained) {
        if (phase_ != Phase::Draining || !drained)
            return false;
        Reset();
        return true;
    }

private:
    enum class Phase { Idle, Listening, Waiting, Speaking, Draining };
    Phase phase_ = Phase::Idle;
};
