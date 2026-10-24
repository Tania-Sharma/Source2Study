from backend.ai.context_adapter import build_resource_context


def test_build_resource_context():

    rag_output = [
        {
            "text": "Normalization reduces redundancy.",
            "metadata": {
                "source": "DBMS.pdf",
                "page": 10,
            },
            "score": 0.92,
        },
        {
            "text": "1NF requires atomic values.",
            "metadata": {
                "source": "DBMS.pdf",
                "page": 11,
            },
            "score": 0.87,
        },
    ]

    context = build_resource_context(
        query="What is normalization?",
        retrieved_chunks=rag_output,
    )

    assert context.query == "What is normalization?"
    assert len(context.retrieved_chunks) == 2

    assert (
        context.retrieved_chunks[0].text
        == "Normalization reduces redundancy."
    )

    assert context.retrieved_chunks[0].score == 0.92

    assert context.get_sources() == ["DBMS.pdf"]