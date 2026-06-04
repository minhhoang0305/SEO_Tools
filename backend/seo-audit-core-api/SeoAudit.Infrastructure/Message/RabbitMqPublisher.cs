using System.Text;
using System.Text.Json;
using FirebaseAdmin.Messaging;
using RabbitMQ.Client;
using SeoAudit.Application.Interfaces;

namespace SeoAudit.Infrastructure.Messaging;


public class RabbitMqPublisher : IMessagePublisher
{
    private readonly IConnectionFactory _factory;
    private string ExchangeName = "audit.exchange";

    public RabbitMqPublisher(
        IConnectionFactory factory)
    {
        _factory = factory;
    }

    public async Task PublishAsync<T>(
        string routingkey,
        T message,
        CancellationToken cancellationToken = default)
    {
        await using var connection =
            await _factory.CreateConnectionAsync(cancellationToken);

        await using var channel =
            await connection.CreateChannelAsync(cancellationToken: cancellationToken);

        await channel.ExchangeDeclareAsync(
            exchange: ExchangeName,
            type: ExchangeType.Topic,
            durable: true,
            autoDelete: false,
            cancellationToken: cancellationToken
        );

        var body = Encoding.UTF8.GetBytes(
            JsonSerializer.Serialize(message));

        await channel.BasicPublishAsync(
            exchange: ExchangeName,
            routingKey: "audit.created",
            mandatory: false,
            body: body,
            cancellationToken: cancellationToken);
    }
}