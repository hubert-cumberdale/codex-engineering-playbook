#include "GazeIntentResolver.h"

namespace
{
const FGazeIntentSceneTarget* ResolveBestTarget(
    const TArray<FGazeIntentSceneTarget>& Targets,
    const FVector2D& Point,
    TFunctionRef<bool(const FGazeIntentSceneTarget&)> Predicate
)
{
    TArray<const FGazeIntentSceneTarget*> Matches;
    for (const FGazeIntentSceneTarget& Target : Targets)
    {
        if (!Target.ScreenRegion.Contains(Point))
        {
            continue;
        }

        if (!Predicate(Target))
        {
            continue;
        }

        Matches.Add(&Target);
    }

    if (Matches.Num() == 0)
    {
        return nullptr;
    }

    Matches.Sort([](const FGazeIntentSceneTarget* A, const FGazeIntentSceneTarget* B)
    {
        if (A->Priority != B->Priority)
        {
            return A->Priority > B->Priority;
        }
        return A->Id < B->Id;
    });

    return Matches[0];
}

FString ResolveUiZone(const TArray<FGazeUiFocusZone>& Zones, const FVector2D& Point)
{
    for (const FGazeUiFocusZone& Zone : Zones)
    {
        if (Zone.ScreenRegion.Contains(Point))
        {
            return Zone.Name;
        }
    }

    return FString();
}

} // namespace

FGazeIntentOutput FGazeIntentResolver::Resolve(
    const FGazeSampleNormalized& Sample,
    const FGazeIntentResolverSettings& Settings,
    const FGazeIntentSceneModel& SceneModel
)
{
    if (IsSuppressed(Sample, Settings))
    {
        return FGazeIntentOutput::MakeNullIntent();
    }

    const FVector2D Point(Sample.gaze_x, Sample.gaze_y);
    FGazeIntentOutput Output = FGazeIntentOutput::MakeNullIntent();

    const FGazeIntentSceneTarget* AimTarget = ResolveBestTarget(
        SceneModel.Targets,
        Point,
        [](const FGazeIntentSceneTarget& Target)
        {
            return Target.bAimable;
        }
    );

    if (AimTarget != nullptr)
    {
        Output.AimIntentTarget = FAimIntentTarget::MakeActor(AimTarget->Id);
    }

    const FGazeIntentSceneTarget* InteractTarget = ResolveBestTarget(
        SceneModel.Targets,
        Point,
        [](const FGazeIntentSceneTarget& Target)
        {
            return Target.bInteractable || Target.bUiElement;
        }
    );

    if (InteractTarget != nullptr)
    {
        Output.InteractIntentTarget = InteractTarget->bUiElement
            ? FInteractIntentTarget::MakeUiElement(InteractTarget->Id)
            : FInteractIntentTarget::MakeActor(InteractTarget->Id);
    }

    Output.UIFocusZone = ResolveUiZone(SceneModel.UiZones, Point);
    return Output;
}

bool FGazeIntentResolver::IsSuppressed(const FGazeSampleNormalized& Sample, const FGazeIntentResolverSettings& Settings)
{
    if (!Settings.bEnabled)
    {
        return true;
    }

    if (Settings.Provider == EGazeProviderSource::Null)
    {
        return true;
    }

    if (!Sample.present)
    {
        return true;
    }

    return Sample.confidence < FMath::Clamp(Settings.ConfidenceThreshold, 0.0f, 1.0f);
}
