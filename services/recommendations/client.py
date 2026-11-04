import grpc
from services.recommendations import recommendation_pb2, recommendation_pb2_grpc

def recommend_therapists(specialization_id, therapists):
    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        client = recommendation_pb2_grpc.RecommendationServiceStub(channel)
        messages = []

        for therapist in therapists:
            spec_ids = []
            for spec in therapist.specializations:
                spec_ids.append(spec.id)
            messages.append(recommendation_pb2.Therapist(
                id = therapist.id,
                specialization_ids=spec_ids,
                experience_years=therapist.experience_years
            ))
        request = recommendation_pb2.RecommendRequest(
            specialization_id=specialization_id,
            therapists=messages
        )
        response = client.Recommend(request, timeout=5)

    return list(response.therapist_ids)