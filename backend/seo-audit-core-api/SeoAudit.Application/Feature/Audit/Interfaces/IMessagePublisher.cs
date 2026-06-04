namespace SeoAudit.Application.Interfaces;

public interface IMessagePublisher
{
    Task PublishAsync<T>(
        string routingKey,
        T message,
        CancellationToken cancellationToken = default);
}