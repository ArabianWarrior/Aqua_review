import { VOError } from "../../shared/value-objects/error.js";

export class WaterError extends VOError {}

export class InvalidityReasonsForWaterError extends WaterError {}

export class Water {
    constructor(readonly milliliters: number) {
        if (new Set(invalidityReasonsFor(milliliters)).size !== 0)
            throw new InvalidityReasonsForWaterError();
    }
}

export enum InvalidityReasons { negativeAmount, floatAmount, nanAmount }

export function *invalidityReasonsFor(milliliters: number): Generator<InvalidityReasons, void, void> {
    if (isNaN(milliliters)) {
        yield InvalidityReasons.nanAmount;
        return;
    }

    if (milliliters < 0)
        yield InvalidityReasons.negativeAmount;

    if (!Number.isInteger(milliliters))
        yield InvalidityReasons.floatAmount;
}

export class InvalidWaterError extends WaterError {}

export class NoReasonsForInvalidWaterError extends InvalidWaterError {}

export class InvalidWater {
    constructor(
        readonly milliliters: number,
        readonly reasons: Set<InvalidityReasons>,
    ) {
        Object.freeze(this.reasons);

        if (this.reasons.size === 0)
            throw new NoReasonsForInvalidWaterError();
    }
}

export type AnyWater = Water | InvalidWater;

export function anyWith(milliliters: number): AnyWater {
    let reasons = new Set(invalidityReasonsFor(milliliters));

    if (reasons.size !== 0)
        return new InvalidWater(milliliters, reasons);

    return new Water(milliliters);
}

export function isInvalid(water: AnyWater): water is InvalidWater {
    return water instanceof InvalidWater;
}
