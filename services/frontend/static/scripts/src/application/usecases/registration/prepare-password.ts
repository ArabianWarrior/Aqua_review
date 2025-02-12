import * as _views from "../../ports/views.js";
import * as _password from "../../../domains/access/value-objects/password.js";

export function execute(
    passwordText: string,
    passwordView: _views.OptionalPositiveView,
    notificationView: _views.RegistrationNotificationView,
): void {
    let password = _password.Password.with(passwordText);

    if (password.isWeak) {
        passwordView.redrawNeutral();
        notificationView.redrawForInvalidPasswordHint();
    }
    else {
        passwordView.redrawOk();
        notificationView.redrawForValidPasswordHint();
    }
}
