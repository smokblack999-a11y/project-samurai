package ai

type Decision string

const (
	DraftOnly      Decision = "draft_only"
	HumanRequired  Decision = "human_required"
	AllowSend      Decision = "allow_send"
)

func Evaluate(confidence float64, sensitive, explicitApproval bool) Decision {
	if sensitive {
		return HumanRequired
	}
	if confidence < 0.90 {
		return HumanRequired
	}
	if !explicitApproval {
		return DraftOnly
	}
	return AllowSend
}
