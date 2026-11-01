
from concurrent import futures

import grpc

import recommendation_pb2
import recommendation_pb2_grpc


class RecommendationService(
    recommendation_pb2_grpc.RecommendationServiceServicer
):
    def Recommend(self, request, context):
        print(
            f"Получен запрос. "
            f"Специализация: {request.specialization_id}"
        )

        suitable_therapists = []

        for therapist in request.therapists:
            if request.specialization_id in therapist.specialization_ids:
                suitable_therapists.append(therapist)

        suitable_therapists.sort(
            key=lambda therapist: therapist.experience_years,
            reverse=True
        )

        therapist_ids = [
            therapist.id for therapist in suitable_therapists
        ]

        print(f"Рекомендованные логопеды: {therapist_ids}")

        return recommendation_pb2.RecommendResponse(
            therapist_ids=therapist_ids
        )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    recommendation_pb2_grpc.add_RecommendationServiceServicer_to_server(
        RecommendationService(),
        server
    )

    server.add_insecure_port("127.0.0.1:50051")
    server.start()

    print("gRPC-сервер запущен на 127.0.0.1:50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
