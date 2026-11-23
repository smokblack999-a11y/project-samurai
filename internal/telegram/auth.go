package telegram

type AuthState string

const (
	AuthWaitParameters AuthState = "wait_parameters"
	AuthWaitPhone      AuthState = "wait_phone"
	AuthWaitCode       AuthState = "wait_code"
	AuthWaitPassword   AuthState = "wait_password"
	AuthReady          AuthState = "ready"
	AuthError          AuthState = "error"
)

type AuthMachine struct {
	State AuthState
}

func NewAuthMachine() *AuthMachine {
	return &AuthMachine{State: AuthWaitParameters}
}

func (m *AuthMachine) Apply(state AuthState) {
	m.State = state
}

func (m *AuthMachine) Ready() bool {
	return m.State == AuthReady
}
