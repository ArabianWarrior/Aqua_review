import * as views from "../../application/ports/views.js";
import * as _username from "../../domains/access/value-objects/username.js";
import * as _password from "../../domains/access/value-objects/password.js";
import * as _credentials from "../../domains/access/value-objects/credentials.js";
import * as _weight from "../../domains/water-recording/value-objects/weight.js";
import * as _waterBalance from "../../domains/water-recording/value-objects/water-balance.js";
import * as _glass from "../../domains/water-recording/value-objects/glass.js";

export const pageView: views.WindowView = {
    redrawToLogin(): void {
        window.location.assign("/sign-in");
    },

    redrawForMainInteractions(): void {
        window.location.assign("/");
    },
}

export class OptionalPositiveCSSView implements views.OptionalPositiveView {
    constructor(
        private _element: HTMLElement,
        private _classNameWhenOk: string,
        private _classNameWhenNeutral: string,
    ) {}

    redrawOk(): void {
        this._element.className = this._classNameWhenOk;
    }

    redrawNeutral(): void {
        this._element.className = this._classNameWhenNeutral;
    }
}

export class TernaryCSSView implements views.TernaryView {
    constructor(
        private _element: HTMLElement,
        private _classNameWhenOk: string,
        private _classNameWhenNeutral: string,
        private _classNameWhenBad: string,
    ) {}

    redrawOk(): void {
        this._element.className = this._classNameWhenOk;
    }

    redrawNeutral(): void {
        this._element.className = this._classNameWhenNeutral;
    }

    redrawBad(): void {
        this._element.className = this._classNameWhenBad;
    }
}

export abstract class DefaultNotificationCSSView {
    constructor(
        protected _notificationElement: HTMLElement,
        protected _textElement: HTMLElement,
    ) {}

    redrawInvisible(): void {
        this._notificationElement.style.display = "none";
        this._textElement.innerText = "";
    }

    redrawTryAgainLater(): void {
        this._textElement.innerText = "Что то пошло не по плану, попробуйте когда нибудь потом!";
        this._redrawBad();
        this._redrawVisible();
    }

    protected _redrawVisible(): void {
        this._notificationElement.style.display = "unset";
    }

    protected _redrawBad(): void {
        this._notificationElement.className = "default-bad-notification";
    }

    protected _redrawNeutral(): void {
        this._notificationElement.className = "default-neutral-notification";
    }

    protected _redrawOk(): void {
        this._notificationElement.className = "default-ok-notification";
    }
}

export class LoginDefaultNotificationCSSView extends DefaultNotificationCSSView implements views.LoginNotificationView {
    redrawInvisible(): void {
        this._notificationElement.style.display = "none";
        this._textElement.innerText = "";
    }

    redrawNoUserWithUsername(_: _username.AnyUsername): void {
        this._textElement.innerText = "Пользователя с таким именем нет";
        this._redrawBad();
        this._redrawVisible();
    }

    redrawInvalidCredentials(_: _credentials.Credentials): void {
        this._textElement.innerText = "Неправильный пароль";
        this._redrawBad();
        this._redrawVisible();
    }

    redrawLastTimeThereWasNoUserNamed(_: _username.AnyUsername): void {
        this._textElement.innerText = "В прошлых попытках пользователя с таким именем не было";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawLastTimeThereWasNoUserWithCredentials(_: _credentials.Credentials): void {
        this._textElement.innerText = "В прошлых попытках такой пароль не подошёл";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawInvalidUsername(_: _username.AnyUsername): void {
        this._textElement.innerText = "Не может быть пользователя с таким именем";
        this._redrawBad();
        this._redrawVisible();
    }

    redrawInvalidPassword(_: _password.Password): void {
        this._textElement.innerText = "Не может быть пользователя с таким паролем";
        this._redrawBad();
        this._redrawVisible();
    }
}

export class RegistrationDefaultNotificationCSSView extends DefaultNotificationCSSView implements views.RegistrationNotificationView {
    redrawForInvalidUsernameHint(): void {
        this._textElement.innerText = "Имя, которое должно иметь хотя бы один символ";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawForValidUsernameHint(): void {
        this._textElement.innerText = "Имя с хотя бы одним символом";
        this._redrawOk();
        this._redrawVisible();
    }

    redrawForTakenUsernameHint(): void {
        this._textElement.innerText = "Имя, занятое другим пользователем";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawUsernameTaken(_: _username.AnyUsername): void {
        this._textElement.innerText = "Имя уже занято";
        this._redrawBad();
        this._redrawVisible();
    }

    redrawForInvalidPasswordHint(): void {
        let element1 = document.createElement("li");
        let element2 = document.createElement("li");
        let element3 = document.createElement("li");

        element1.innerText = "не менее 8 символов";
        element2.innerText = "любые цифры";
        element3.innerText = "буквы в нижнем и в верхнем регистрах";

        this._textElement.innerText = "Пароль, который должен иметь:";
        this._textElement.appendChild(element1);
        this._textElement.appendChild(element2);
        this._textElement.appendChild(element3);

        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawForValidPasswordHint(): void {
        let element1 = document.createElement("li");
        let element2 = document.createElement("li");
        let element3 = document.createElement("li");

        element1.innerText = "не менее 8 символов";
        element2.innerText = "любые цифры";
        element3.innerText = "буквы в нижнем и в верхнем регистрах";

        this._textElement.innerText = "Пароль имеющий:";
        this._textElement.appendChild(element1);
        this._textElement.appendChild(element2);
        this._textElement.appendChild(element3);

        this._redrawOk();
        this._redrawVisible();
    }

    redrawForValidWeightWithTargetHint(): void {
        this._textElement.innerText = "Опциональный вес в виде целого положительного числа, измеряемым в килограммах";
        this._redrawOk();
        this._redrawVisible();
    }

    redrawForInvalidWeightWithTargetHint(): void {
        this._textElement.innerText = "Опциональный вес, который может быть целым положительным числом, измеряемым в килограммах";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawForValidWeightWithoutTargetHint(): void {
        this._textElement.innerText = "Вес в виде целого положительного числа от 30 до 150 кг включительно";
        this._redrawOk();
        this._redrawVisible();
    }

    redrawForInvalidWeightWithoutTargetHint(): void {
        this._textElement.innerText = "Вес, который должен быть целым положительным числом от 30 до 150 кг включительно";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawForValidTargetWithWeightHint(): void {
        this._textElement.innerText = "Количество воды в миллилитрах, в виде целого положительного числа, которое вы хотите выпивать за сутки, может отсутствовать";
        this._redrawOk();
        this._redrawVisible();
    }

    redrawForInvalidTargetWithWeightHint(): void {
        this._textElement.innerText = "Количество воды в миллилитрах, которое вы хотите выпивать за сутки, может отсутствовать. Если указано, должно быть целым положительным числом";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawForValidTargetWithoutWeightHint(): void {
        this._textElement.innerText = "Количество воды в миллилитрах, в виде целого положительного числа, которое вы хотите выпивать за сутки";
        this._redrawOk();
        this._redrawVisible();
    }

    redrawForInvalidTargetWithoutWeightHint(): void {
        this._textElement.innerText = "Количество воды в миллилитрах, которое вы хотите выпивать за сутки, должно быть целым положительным числом";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawForValidGlassHint(): void {
        this._textElement.innerText = "Количество воды в миллилитрах, в виде целого положительного числа, которое вы обычно выпиваете, может отсутствовать";
        this._redrawOk();
        this._redrawVisible();
    }

    redrawForInvalidGlassHint(): void {
        this._textElement.innerText = "Количество воды в миллилитрах, которое вы обычно выпиваете, может отсутствовать. Если указано, должно быть целым положительным числом";
        this._redrawNeutral();
        this._redrawVisible();
    }

    redrawAccountCreated(): void {
        this._textElement.innerText = "Аккаунт создан!";
        this._redrawOk();
        this._redrawVisible();
    }

    redrawBadInput(): void {
        this._textElement.innerText = "Для создания аккаунта все поля должны быть заполнены верно";
        this._redrawBad();
        this._redrawVisible();
    }
}
